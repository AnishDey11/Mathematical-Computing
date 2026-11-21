
import tkinter as tk
from tkinter import ttk, messagebox
import math


class AdjacencyMatrixApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Graph Adjacency Matrix Generator")
        self.root.configure(bg="#101827")

        # Open maximized
        try:
            self.root.state("zoomed")
        except tk.TclError:
            self.root.geometry("1200x850")

        self.bg = "#101827"
        self.panel = "#1c293b"
        self.input_bg = "#26364b"
        self.accent = "#38bdf8"
        self.text = "#f1f5f9"
        self.muted = "#94a3b8"
        self.green = "#34d399"

        self.edge_entries = []
        self.matrix = []

        self.setup_styles()
        self.create_main_scroll()
        self.create_interface()

        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.exit_fullscreen)

        self.generate_fields()

    # ---------------- STYLES ----------------

    def setup_styles(self):

        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Treeview",
            background="#26364b",
            foreground="white",
            fieldbackground="#26364b",
            rowheight=34,
            font=("Segoe UI", 10)
        )

        style.configure(
            "Treeview.Heading",
            background="#334155",
            foreground="white",
            font=("Segoe UI", 10, "bold")
        )

        style.map(
            "Treeview",
            background=[("selected", "#0369a1")],
            foreground=[("selected", "white")]
        )

    # ---------------- FULL WINDOW SCROLL ----------------

    def create_main_scroll(self):

        self.main_canvas = tk.Canvas(
            self.root,
            bg=self.bg,
            highlightthickness=0
        )

        self.main_scrollbar = ttk.Scrollbar(
            self.root,
            orient="vertical",
            command=self.main_canvas.yview
        )

        self.main_canvas.configure(
            yscrollcommand=self.main_scrollbar.set
        )

        self.main_scrollbar.pack(side="right", fill="y")
        self.main_canvas.pack(
            side="left", fill="both", expand=True
        )

        self.main_frame = tk.Frame(
            self.main_canvas,
            bg=self.bg
        )

        self.window_id = self.main_canvas.create_window(
            (0, 0),
            window=self.main_frame,
            anchor="nw"
        )

        self.main_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(
                scrollregion=self.main_canvas.bbox("all")
            )
        )

        self.main_canvas.bind(
            "<Configure>",
            lambda e: self.main_canvas.itemconfigure(
                self.window_id, width=e.width
            )
        )

        # Mouse wheel scrolling
        self.main_canvas.bind_all(
            "<MouseWheel>", self.mouse_scroll
        )

    def mouse_scroll(self, event):

        widget = self.root.winfo_containing(
            event.x_root, event.y_root
        )

        if widget is None:
            return

        # Allow inner canvases and Treeviews to handle
        # their own scrolling.
        current = widget

        while current is not None:
            if current in (
                self.edge_canvas,
                self.matrix_table
            ) if hasattr(self, "edge_canvas") and hasattr(
                self, "matrix_table"
            ) else ():
                return
            current = getattr(current, "master", None)

        self.main_canvas.yview_scroll(
            int(-event.delta / 120), "units"
        )

    def toggle_fullscreen(self, event=None):

        self.root.attributes(
            "-fullscreen",
            not self.root.attributes("-fullscreen")
        )

    def exit_fullscreen(self, event=None):
        self.root.attributes("-fullscreen", False)

    # ---------------- MAIN INTERFACE ----------------

    def create_interface(self):

        # Header
        header = tk.Frame(
            self.main_frame,
            bg=self.bg
        )
        header.pack(fill="x", padx=30, pady=(22, 15))

        tk.Label(
            header,
            text="GRAPH ADJACENCY MATRIX",
            font=("Segoe UI", 25, "bold"),
            bg=self.bg,
            fg=self.text
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Graph construction and adjacency matrix visualization",
            font=("Segoe UI", 11),
            bg=self.bg,
            fg=self.muted
        ).pack(anchor="w", pady=5)

        # Fullscreen information
        tk.Label(
            header,
            text="F11: Toggle Fullscreen     ESC: Exit Fullscreen",
            font=("Segoe UI", 9),
            bg=self.bg,
            fg=self.accent
        ).pack(anchor="w", pady=4)

        self.create_configuration()
        self.create_edge_section()
        self.create_actions()
        self.create_output_section()

    # ---------------- CONFIGURATION ----------------

    def create_configuration(self):

        frame = tk.LabelFrame(
            self.main_frame,
            text=" Graph Configuration ",
            bg=self.panel,
            fg=self.accent,
            font=("Segoe UI", 11, "bold"),
            padx=15,
            pady=15
        )

        frame.pack(fill="x", padx=30, pady=10)

        self.vertices = self.create_entry(
            frame, "Number of Vertices", 5, 0, 0
        )

        self.edge_count = self.create_entry(
            frame, "Number of Edges", 6, 0, 2
        )

        self.directed = tk.BooleanVar(value=False)
        self.weighted = tk.BooleanVar(value=False)
        self.allow_loops = tk.BooleanVar(value=False)

        options = [
            ("Directed Graph", self.directed),
            ("Weighted Graph", self.weighted),
            ("Allow Self-Loops", self.allow_loops)
        ]

        for i, (label, variable) in enumerate(options):

            tk.Checkbutton(
                frame,
                text=label,
                variable=variable,
                bg=self.panel,
                fg=self.text,
                selectcolor=self.input_bg,
                activebackground=self.panel,
                activeforeground="white",
                font=("Segoe UI", 10)
            ).grid(
                row=1, column=i * 2,
                columnspan=2,
                sticky="w",
                padx=10, pady=12
            )

        self.make_button(
            frame,
            "Generate Edge Fields",
            self.generate_fields
        ).grid(
            row=0, column=4,
            padx=15, pady=5
        )

    def create_entry(self, parent, label, default, row, col):

        container = tk.Frame(parent, bg=self.panel)
        container.grid(
            row=row, column=col,
            padx=10, pady=5, sticky="w"
        )

        tk.Label(
            container,
            text=label,
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI", 10)
        ).pack(anchor="w")

        entry = tk.Entry(
            container,
            width=14,
            bg=self.input_bg,
            fg="white",
            insertbackground="white",
            relief="flat",
            font=("Segoe UI", 11)
        )

        entry.pack(pady=5)
        entry.insert(0, str(default))

        return entry

    # ---------------- EDGE INPUT ----------------

    def create_edge_section(self):

        self.edge_frame = tk.LabelFrame(
            self.main_frame,
            text=" Edge Input ",
            bg=self.panel,
            fg=self.accent,
            font=("Segoe UI", 11, "bold"),
            padx=12,
            pady=12
        )

        self.edge_frame.pack(
            fill="x", padx=30, pady=10
        )

        tk.Label(
            self.edge_frame,
            text="Enter the source and destination of each edge. "
                 "Vertices are numbered from 1.",
            bg=self.panel,
            fg=self.muted,
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(0, 10))

        container = tk.Frame(
            self.edge_frame,
            bg=self.panel
        )
        container.pack(fill="both", expand=True)

        self.edge_canvas = tk.Canvas(
            container,
            bg=self.panel,
            height=230,
            highlightthickness=0
        )

        self.edge_vscroll = ttk.Scrollbar(
            container,
            orient="vertical",
            command=self.edge_canvas.yview
        )

        self.edge_hscroll = ttk.Scrollbar(
            container,
            orient="horizontal",
            command=self.edge_canvas.xview
        )

        self.edge_inner = tk.Frame(
            self.edge_canvas,
            bg=self.panel
        )

        self.edge_inner.bind(
            "<Configure>",
            lambda e: self.edge_canvas.configure(
                scrollregion=self.edge_canvas.bbox("all")
            )
        )

        self.edge_canvas.create_window(
            (0, 0),
            window=self.edge_inner,
            anchor="nw"
        )

        self.edge_canvas.configure(
            yscrollcommand=self.edge_vscroll.set,
            xscrollcommand=self.edge_hscroll.set
        )

        self.edge_canvas.grid(
            row=0, column=0, sticky="nsew"
        )

        self.edge_vscroll.grid(
            row=0, column=1, sticky="ns"
        )

        self.edge_hscroll.grid(
            row=1, column=0, sticky="ew"
        )

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

    def generate_fields(self):

        try:
            n = int(self.edge_count.get())

            if not 0 <= n <= 500:
                raise ValueError

        except ValueError:
            messagebox.showerror(
                "Invalid Input",
                "Enter an edge count between 0 and 500."
            )
            return

        for widget in self.edge_inner.winfo_children():
            widget.destroy()

        self.edge_entries = []

        headers = [
            "Edge Number",
            "Source Vertex",
            "Destination Vertex"
        ]

        if self.weighted.get():
            headers.append("Weight")

        for col, heading in enumerate(headers):

            tk.Label(
                self.edge_inner,
                text=heading,
                bg="#334155",
                fg=self.accent,
                font=("Segoe UI", 10, "bold"),
                width=20,
                pady=8
            ).grid(
                row=0, column=col,
                padx=4, pady=4
            )

        # Sample values are loaded when possible
        sample_edges = [
            (1, 2, 1),
            (1, 3, 1),
            (2, 3, 1),
            (2, 4, 1),
            (3, 5, 1),
            (2, 1, 1)
        ]

        for i in range(n):

            tk.Label(
                self.edge_inner,
                text=f"Edge {i+1}",
                bg=self.panel,
                fg=self.text,
                font=("Segoe UI", 10),
                width=20
            ).grid(
                row=i+1, column=0,
                padx=4, pady=5
            )

            values = (
                sample_edges[i]
                if i < len(sample_edges)
                else ("", "", "1")
            )

            entries = []

            for j in range(2):

                entry = tk.Entry(
                    self.edge_inner,
                    width=20,
                    bg=self.input_bg,
                    fg="white",
                    insertbackground="white",
                    relief="flat",
                    font=("Segoe UI", 10)
                )

                entry.grid(
                    row=i+1, column=j+1,
                    padx=4, pady=5
                )

                entry.insert(0, str(values[j]))
                entries.append(entry)

            if self.weighted.get():

                weight = tk.Entry(
                    self.edge_inner,
                    width=20,
                    bg=self.input_bg,
                    fg="white",
                    insertbackground="white",
                    relief="flat"
                )

                weight.grid(
                    row=i+1, column=3,
                    padx=4, pady=5
                )

                weight.insert(0, str(values[2]))
                entries.append(weight)

            self.edge_entries.append(entries)

    # ---------------- BUTTONS ----------------

    def create_actions(self):

        frame = tk.Frame(
            self.main_frame,
            bg=self.bg
        )

        frame.pack(fill="x", padx=30, pady=15)

        self.make_button(
            frame,
            "CREATE ADJACENCY MATRIX",
            self.create_matrix,
            self.green
        ).pack(side="left", padx=5)

        self.make_button(
            frame,
            "RESET",
            self.reset,
            "#475569"
        ).pack(side="left", padx=5)

        self.make_button(
            frame,
            "CLEAR OUTPUT",
            self.clear_output,
            "#475569"
        ).pack(side="left", padx=5)

    def make_button(self, parent, text, command, color=None):

        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=color or self.accent,
            fg="#101827",
            activebackground="#0284c7",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            font=("Segoe UI", 10, "bold"),
            padx=16,
            pady=10
        )

    # ---------------- MATRIX OUTPUT ----------------

    def create_output_section(self):

        self.output_frame = tk.LabelFrame(
            self.main_frame,
            text=" Adjacency Matrix Output ",
            bg=self.panel,
            fg=self.accent,
            font=("Segoe UI", 11, "bold"),
            padx=12,
            pady=12
        )

        self.output_frame.pack(
            fill="both", expand=True,
            padx=30, pady=10
        )

        tk.Label(
            self.output_frame,
            text="Matrix Visualization",
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", pady=8)

        # Matrix table and scrollbars
        table_container = tk.Frame(
            self.output_frame,
            bg=self.panel
        )
        table_container.pack(
            fill="both", expand=True
        )

        self.matrix_table = ttk.Treeview(
            table_container,
            show="headings",
            height=12
        )

        self.matrix_vscroll = ttk.Scrollbar(
            table_container,
            orient="vertical",
            command=self.matrix_table.yview
        )

        self.matrix_hscroll = ttk.Scrollbar(
            table_container,
            orient="horizontal",
            command=self.matrix_table.xview
        )

        self.matrix_table.configure(
            yscrollcommand=self.matrix_vscroll.set,
            xscrollcommand=self.matrix_hscroll.set
        )

        self.matrix_table.grid(
            row=0, column=0, sticky="nsew"
        )

        self.matrix_vscroll.grid(
            row=0, column=1, sticky="ns"
        )

        self.matrix_hscroll.grid(
            row=1, column=0, sticky="ew"
        )

        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)

        # Information section
        self.result_label = tk.Label(
            self.output_frame,
            text="Generate a matrix to see the results.",
            bg=self.panel,
            fg=self.muted,
            font=("Segoe UI", 10),
            justify="left",
            anchor="w"
        )

        self.result_label.pack(
            fill="x", pady=12
        )

        self.edge_result = tk.Text(
            self.output_frame,
            height=5,
            bg=self.input_bg,
            fg=self.text,
            font=("Consolas", 10),
            relief="flat",
            wrap="word"
        )

        self.edge_result.pack(
            fill="x", pady=5
        )

        self.edge_result.insert(
            "1.0", "Processed edge list will appear here."
        )
        self.edge_result.configure(state="disabled")

    # ---------------- MATRIX ALGORITHM ----------------

    def create_matrix(self):

        try:
            n = int(self.vertices.get())
            m = int(self.edge_count.get())

            if not 1 <= n <= 100:
                raise ValueError(
                    "Vertices must be between 1 and 100."
                )

            if not 0 <= m <= 500:
                raise ValueError(
                    "Edges must be between 0 and 500."
                )

            if len(self.edge_entries) != m:
                raise ValueError(
                    "Click Generate Edge Fields after "
                    "changing the number of edges."
                )

        except ValueError as error:
            messagebox.showerror("Input Error", str(error))
            return

        directed = self.directed.get()
        weighted = self.weighted.get()
        loops = self.allow_loops.get()

        matrix = [[0] * n for _ in range(n)]

        seen = set()
        duplicates = []
        processed = []

        for index, entries in enumerate(self.edge_entries):

            try:
                u = int(entries[0].get())
                v = int(entries[1].get())

                if not (1 <= u <= n and 1 <= v <= n):
                    raise ValueError(
                        f"Edge {index+1}: Vertices must be "
                        f"between 1 and {n}."
                    )

                if u == v and not loops:
                    raise ValueError(
                        f"Edge {index+1}: Self-loop is disabled."
                    )

                if weighted:
                    w = float(entries[2].get())

                    if not math.isfinite(w):
                        raise ValueError(
                            "Edge weights must be finite numbers."
                        )
                else:
                    w = 1

                # Convert to zero-based indexing
                i = u - 1
                j = v - 1

                # Duplicate detection
                if directed:
                    key = (i, j)
                else:
                    key = (min(i, j), max(i, j))

                if key in seen:
                    duplicates.append((u, v))
                    continue

                seen.add(key)

                # Insert edge
                matrix[i][j] = w

                # Undirected graph
                if not directed:
                    matrix[j][i] = w

                processed.append((u, v, w))

            except ValueError as error:
                messagebox.showerror(
                    "Edge Input Error", str(error)
                )
                return

        self.matrix = matrix

        self.display_matrix(matrix, n)
        self.display_statistics(
            n, m, processed, duplicates, directed, weighted
        )

    # ---------------- DISPLAY MATRIX ----------------

    def display_matrix(self, matrix, n):

        self.matrix_table.delete(
            *self.matrix_table.get_children()
        )

        columns = ["Vertex"] + [
            f"V{i+1}" for i in range(n)
        ]

        self.matrix_table["columns"] = columns

        for col in columns:

            self.matrix_table.heading(
                col, text=col
            )

            self.matrix_table.column(
                col,
                width=90,
                minwidth=65,
                anchor="center",
                stretch=False
            )

        for i in range(n):

            values = [
                f"V{i+1}"
            ] + matrix[i]

            self.matrix_table.insert(
                "", "end",
                values=values
            )

    # ---------------- STATISTICS ----------------

    def display_statistics(
        self, n, m, processed,
        duplicates, directed, weighted
    ):

        self.result_label.config(
            text=(
                f"Vertices: {n}     "
                f"Input Edges: {m}     "
                f"Unique Edges: {len(processed)}\n"
                f"Graph: {'Directed' if directed else 'Undirected'}"
                f"     Weighted: {'Yes' if weighted else 'No'}"
                f"     Repeated Edges: {len(duplicates)}"
            ),
            fg=self.green
        )

        output = "PROCESSED EDGE LIST\n"
        output += "-" * 45 + "\n"

        for u, v, w in processed:

            if weighted:
                output += f"{u} -> {v}  (Weight: {w})\n"
            else:
                output += f"{u} -> {v}\n"

        if duplicates:
            output += "\nREPEATED EDGES IGNORED\n"

            for u, v in duplicates:
                output += f"{u} -> {v}\n"
        else:
            output += "\nNo repeated edges detected.\n"

        self.edge_result.configure(state="normal")
        self.edge_result.delete("1.0", tk.END)
        self.edge_result.insert("1.0", output)
        self.edge_result.configure(state="disabled")

    # ---------------- CLEAR / RESET ----------------

    def clear_output(self):

        self.matrix_table.delete(
            *self.matrix_table.get_children()
        )

        self.result_label.config(
            text="Output cleared.",
            fg=self.muted
        )

        self.edge_result.configure(state="normal")
        self.edge_result.delete("1.0", tk.END)
        self.edge_result.insert("1.0", "No output available.")
        self.edge_result.configure(state="disabled")

    def reset(self):

        self.vertices.delete(0, tk.END)
        self.vertices.insert(0, "5")

        self.edge_count.delete(0, tk.END)
        self.edge_count.insert(0, "6")

        self.directed.set(False)
        self.weighted.set(False)
        self.allow_loops.set(False)

        self.clear_output()
        self.generate_fields()

        self.main_canvas.yview_moveto(0)


# ---------------- MAIN ----------------

if __name__ == "__main__":

    root = tk.Tk()

    app = AdjacencyMatrixApp(root)

    root.mainloop()
