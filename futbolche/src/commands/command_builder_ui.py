import json
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, List, Callable, Any

from .command_tree import CommandNode, CommandTreeBuilder



_FieldWidget = Dict[str, Any]


class CommandBuilderPanel(ttk.Frame):
    def __init__(self, parent, on_execute: Optional[Callable] = None, **kwargs):
        super().__init__(parent, **kwargs)
        self._tree_builder = CommandTreeBuilder()
        self._tree = self._tree_builder.build_tree()
        self._current_node: Optional[CommandNode] = self._tree
        self._on_execute = on_execute
        self._param_widgets: Dict[str, _FieldWidget] = {}

        self._build_ui()
        self._show_node(self._tree)

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        header = ttk.Label(self, text="Команден строител", font=("Arial", 12, "bold"))
        header.grid(row=0, column=0, pady=(5, 2), padx=5, sticky="w")

        self._breadcrumb = ttk.Label(self, text="", font=("Arial", 9))
        self._breadcrumb.grid(row=1, column=0, pady=(0, 5), padx=5, sticky="w")

        canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self._scroll_frame = ttk.Frame(canvas)

        self._scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self._scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=2, column=0, sticky="nsew", padx=5)
        scrollbar.grid(row=2, column=1, sticky="ns")

        self._scroll_frame.columnconfigure(0, weight=1)

        preview_frame = ttk.LabelFrame(self, text="Преглед на интента", padding=5)
        preview_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=(5, 2))
        preview_frame.columnconfigure(0, weight=1)

        self._preview_text = tk.Text(preview_frame, height=5, font=("Consolas", 9),
                                     bg="#1e1e1e", fg="#d4d4d4", borderwidth=0)
        self._preview_text.grid(row=0, column=0, sticky="ew")
        self._preview_text.insert("1.0", "{}")
        self._preview_text.config(state=tk.DISABLED)

        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=5)

        self._back_btn = ttk.Button(btn_frame, text="◀ Назад", command=self._go_back)
        self._back_btn.pack(side=tk.LEFT, padx=2)

        self._execute_btn = ttk.Button(btn_frame, text="▶ Изпълни", command=self._execute)
        self._execute_btn.pack(side=tk.LEFT, padx=2)

    def _clear_options(self):
        for w in self._scroll_frame.winfo_children():
            w.destroy()
        self._param_widgets.clear()

    def _update_breadcrumb(self):
        if not self._current_node:
            self._breadcrumb.config(text="")
            return
        path = self._current_node.path_from_root()
        parts = []
        for node in path:
            if node.type == "root":
                parts.append("Команди")
            else:
                parts.append(node.label)
        self._breadcrumb.config(text=" > ".join(parts))

    def _show_node(self, node: CommandNode):
        self._current_node = node
        self._clear_options()
        self._update_breadcrumb()

        if node.type in ("root", "category"):
            self._show_children_as_buttons(node)
        elif node.type == "command":
            self._show_parameter_form(node)
        else:
            self._show_children_as_buttons(node)

        self._update_preview()

    def _show_children_as_buttons(self, parent: CommandNode):
        self._back_btn.config(state=tk.NORMAL if parent.parent else tk.DISABLED)

        for child in parent.children:
            btn = tk.Button(
                self._scroll_frame,
                text=child.label,
                command=lambda c=child: self._show_node(c),
                bg="#3c3c3c", fg="#ffffff",
                font=("Arial", 10),
                borderwidth=0, padx=15, pady=10,
                cursor="hand2", anchor="w",
                justify=tk.LEFT,
            )
            btn.pack(fill=tk.X, padx=5, pady=2)

            if child.type == "command" and child.metadata.get("example"):
                example_label = tk.Label(
                    self._scroll_frame,
                    text=f"  {child.metadata['example']}",
                    font=("Arial", 8),
                    fg="#888888", bg="#252526",
                    anchor="w", justify=tk.LEFT,
                )
                example_label.pack(fill=tk.X, padx=(25, 5))

    def _show_parameter_form(self, node: CommandNode):
        self._back_btn.config(state=tk.NORMAL)

        params = [c for c in node.children if c.type == "parameter"]

        if not params:
            no_params = ttk.Label(self._scroll_frame, text="Няма параметри. Натиснете 'Изпълни'.",
                                  font=("Arial", 10))
            no_params.pack(pady=10)
            self._execute_btn.config(state=tk.NORMAL)
            return

        for i, param_node in enumerate(params):
            meta = param_node.metadata
            pname = meta.get("param_name", "")
            ptype = meta.get("param_type", "TEXT")
            required = meta.get("required", True)
            enum_values = meta.get("enum_values", [])

            req_mark = "*" if required else ""
            label_text = f"{param_node.label}{req_mark}"
            lbl = ttk.Label(self._scroll_frame, text=label_text, font=("Arial", 10))
            lbl.pack(anchor="w", padx=10, pady=(8, 2))

            if ptype == "ENUM" and enum_values:
                var = tk.StringVar()
                widget = ttk.Combobox(self._scroll_frame, textvariable=var,
                                      values=enum_values, state="readonly")
                widget.pack(fill=tk.X, padx=10, pady=(0, 2))
                if enum_values:
                    var.set(enum_values[0])
            elif ptype == "INTEGER":
                var = tk.StringVar()
                widget = ttk.Spinbox(self._scroll_frame, from_=0, to=999,
                                     textvariable=var, width=10)
                widget.pack(anchor="w", padx=10, pady=(0, 2))
            elif ptype == "FLOAT":
                var = tk.StringVar()
                widget = tk.Entry(self._scroll_frame, textvariable=var, font=("Arial", 10))
                widget.pack(fill=tk.X, padx=10, pady=(0, 2))
            elif ptype == "BOOLEAN":
                var = tk.BooleanVar(value=False)
                widget = ttk.Checkbutton(self._scroll_frame, variable=var)
                widget.pack(anchor="w", padx=10, pady=(0, 2))
            else:
                var = tk.StringVar()
                placeholder = meta.get("placeholder", "")
                widget = tk.Entry(self._scroll_frame, textvariable=var, font=("Arial", 10))
                widget.pack(fill=tk.X, padx=10, pady=(0, 2))

            self._param_widgets[pname] = {"var": var, "widget": widget, "ptype": ptype}
            var.trace_add("write", lambda *_: self._update_preview())

    def _get_var(self, field: _FieldWidget) -> Any:
        return field.get("var")

    def _get_ptype(self, field: _FieldWidget) -> str:
        return str(field.get("ptype", "TEXT"))

    def _collect_params(self) -> Dict[str, str]:
        result = {}
        for pname, field in self._param_widgets.items():
            var = self._get_var(field)
            if not var:
                continue
            raw = var.get()
            if raw is None or (isinstance(raw, str) and not raw.strip()):
                continue
            val = str(raw).strip()
            ptype = self._get_ptype(field)
            if ptype == "BOOLEAN":
                val = str(var.get()).lower()
            result[pname] = val
        return result

    def _build_intent_dict(self) -> Optional[Dict]:
        if not self._current_node or self._current_node.type != "command":
            return None
        params = self._collect_params()
        intent = {"intent": self._current_node.metadata.get("tag", "")}
        if params:
            intent["parameters"] = params
        return intent

    def _update_preview(self):
        intent = self._build_intent_dict()
        text = json.dumps(intent, indent=2, ensure_ascii=False) if intent else "{}"
        self._preview_text.config(state=tk.NORMAL)
        self._preview_text.delete("1.0", tk.END)
        self._preview_text.insert("1.0", text)
        self._preview_text.config(state=tk.DISABLED)

    def _go_back(self):
        if self._current_node and self._current_node.parent:
            self._show_node(self._current_node.parent)

    def _execute(self):
        intent = self._build_intent_dict()
        if not intent:
            messagebox.showwarning("Грешка", "Няма избрана команда.")
            return

        tag = intent["intent"]
        params = intent.get("parameters", {})

        if not params:
            if self._on_execute:
                self._on_execute(tag, None)
            return

        missing = []
        for pname, field in self._param_widgets.items():
            var = self._get_var(field)
            if not var:
                continue
            meta = None
            for child in (self._current_node.children if self._current_node else []):
                if child.metadata.get("param_name") == pname:
                    meta = child.metadata
                    break
            if meta and meta.get("required", True):
                raw = var.get()
                if raw is None or (isinstance(raw, str) and not raw.strip()):
                    missing.append(pname)

        if missing:
            msg = "Попълнете задължителните полета:\n" + "\n".join(f"  - {m}" for m in missing)
            messagebox.showwarning("Невалидни параметри", msg)
            return

        if self._on_execute:
            self._on_execute(tag, params)

    def reset(self):
        self._show_node(self._tree)
