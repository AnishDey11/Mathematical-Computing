
import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque
import math


class BipartiteGraphGUI:

    def __init__(self, root):

        self.root = root
        self.root.title("Bipartite Graph Checker")
        self.root.configure(bg="#101827")

        try:
            self.root.state("zoomed")
        except tk.TclError:
            self.root.geometry("1250x900")

        # Theme colors
        self.bg = "#101827"
        self.panel = "#1c293b"
        self.input_bg = "#26364b"
        self.accent = "#38bdf8"
        self.text = "#f1f5f9"
        self.muted = "#94a3b8"
        self.green = "#34d399"
        self.red = "#fb7185"

        self.edge_entries = []
        self.graph_data = None

        self.setup_style()
        self.create_scrollable_window()
        self.create_interface()

        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.exit_fullscreen)

        self.generate_fields()

    # ==================================================
    # STYLES
    # ==================================================

    def setup_style(self):

        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Treeview",
            background=self.input_bg,
            foreground="white",
            fieldbackground=self.input_bg,
            rowheight=32,
            font=("Segoe UI", 10)
        )

        style.configure(
            "Treeview.Heading",
            background="#334155",
            foreground="white",
            font=("Segoe UI", 10, "bold")
        )

    # ==================================================
    # MAIN SCROLLABLE WINDOW
    # ==================================================

    def create_scrollable_window(self):

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

        self.main_scrollbar.pack(
            side="right",
            fill="y"
        )

        self.main_canvas.pack(
            side="left",
            fill="both",
            expand=True
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
                self.window_id,
                width=e.width
            )
        )

        self.main_canvas.bind_all(
            "<MouseWheel>",
            self.mouse_scroll
        )

    def mouse_scroll(self, event):

        widget = self.root.winfo_containing(
            event.x_root,
            event.y_root
        )

        # Let inner canvases and text widgets
        # handle their own scrolling.
        current = widget

        while current is not None:

            if current in (
                getattr(self, "edge_canvas", None),
                getattr(self, "graph_canvas", None),
                getattr(self, "result_text", None)
            ):
                return

            current = getattr(current, "master", None)

        self.main_canvas.yview_scroll(
            int(-event.delta / 120),
            "units"
        )

    def toggle_fullscreen(self, event=None):

        self.root.attributes(
            "-fullscreen",
            not self.root.attributes("-fullscreen")
        )

    def exit_fullscreen(self, event=None):

        self.root.attributes(
            "-fullscreen",
            False
        )

    # ==================================================
    # MAIN INTERFACE
    # ==================================================

    def create_interface(self):

        # HEADER
        header = tk.Frame(
            self.main_frame,
            bg=self.bg
        )

        header.pack(
            fill="x",
            padx=30,
            pady=(22, 15)
        )

        tk.Label(
            header,
            text="BIPARTITE GRAPH CHECKER",
            font=("Segoe UI", 25, "bold"),
            bg=self.bg,
            fg=self.text
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Graph verification using BFS and two-coloring",
            font=("Segoe UI", 11),
            bg=self.bg,
            fg=self.muted
        ).pack(anchor="w", pady=5)

        tk.Label(
            header,
            text="F11: Fullscreen     ESC: Exit Fullscreen",
            font=("Segoe UI", 9),
            bg=self.bg,
            fg=self.accent
        ).pack(anchor="w", pady=4)

        self.create_configuration()
        self.create_edge_section()
        self.create_buttons()
        self.create_output()

    # ==================================================
    # GRAPH CONFIGURATION
    # ==================================================

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

        frame.pack(
            fill="x",
            padx=30,
            pady=10
        )

        self.vertices = self.make_input(
            frame,
            "Number of Vertices",
            "5",
            0
        )

        self.edge_count = self.make_input(
            frame,
            "Number of Edges",
            "5",
            1
        )

        tk.Label(
            frame,
            text="Graph Type: Undirected",
            bg=self.panel,
            fg=self.green,
            font=("Segoe UI", 10, "bold")
        ).grid(
            row=0,
            column=2,
            padx=25,
            pady=10
        )

        self.make_button(
            frame,
            "Generate Edge Fields",
            self.generate_fields
        ).grid(
            row=0,
            column=3,
            padx=15
        )

    def make_input(self, parent, label, default, col):

        container = tk.Frame(
            parent,
            bg=self.panel
        )

        container.grid(
            row=0,
            column=col,
            padx=10,
            pady=5
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
        entry.insert(0, default)

        return entry

    # ==================================================
    # EDGE INPUT SECTION
    # ==================================================

    def create_edge_section(self):

        self.edge_frame = tk.LabelFrame(
            self.main_frame,
            text=" Enter Graph Edges ",
            bg=self.panel,
            fg=self.accent,
            font=("Segoe UI", 11, "bold"),
            padx=12,
            pady=12
        )

        self.edge_frame.pack(
            fill="x",
            padx=30,
            pady=10
        )

        tk.Label(
            self.edge_frame,
            text="Enter the two vertices connected by each edge. "
                 "Vertex numbering starts from 1.",
            bg=self.panel,
            fg=self.muted,
            font=("Segoe UI", 10)
        ).pack(
            anchor="w",
            pady=8
        )

        container = tk.Frame(
            self.edge_frame,
            bg=self.panel
        )

        container.pack(
            fill="both",
            expand=True
        )

        self.edge_canvas = tk.Canvas(
            container,
            bg=self.panel,
            height=220,
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
            row=0,
            column=0,
            sticky="nsew"
        )

        self.edge_vscroll.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        self.edge_hscroll.grid(
            row=1,
            column=0,
            sticky="ew"
        )

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

    # ==================================================
    # GENERATE EDGE INPUT FIELDS
    # ==================================================

    def generate_fields(self):

        try:

            n = int(self.vertices.get())
            m = int(self.edge_count.get())

            if not 1 <= n <= 100:
                raise ValueError(
                    "Number of vertices must be between 1 and 100."
                )

            if not 0 <= m <= 500:
                raise ValueError(
                    "Number of edges must be between 0 and 500."
                )

        except ValueError as e:

            messagebox.showerror(
                "Input Error",
                str(e)
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

        for col, heading in enumerate(headers):

            tk.Label(
                self.edge_inner,
                text=heading,
                bg="#334155",
                fg=self.accent,
                font=("Segoe UI", 10, "bold"),
                width=22,
                pady=8
            ).grid(
                row=0,
                column=col,
                padx=5,
                pady=5
            )

        # Default sample graph
        sample_edges = [
            (1, 2),
            (1, 3),
            (2, 4),
            (3, 4),
            (4, 5)
        ]

        for i in range(m):

            tk.Label(
                self.edge_inner,
                text=f"Edge {i+1}",
                bg=self.panel,
                fg=self.text,
                width=22,
                font=("Segoe UI", 10)
            ).grid(
                row=i+1,
                column=0,
                padx=5,
                pady=5
            )

            if i < len(sample_edges):
                values = sample_edges[i]
            else:
                values = ("", "")

            entries = []

            for j in range(2):

                entry = tk.Entry(
                    self.edge_inner,
                    width=22,
                    bg=self.input_bg,
                    fg="white",
                    insertbackground="white",
                    relief="flat",
                    font=("Segoe UI", 10)
                )

                entry.grid(
                    row=i+1,
                    column=j+1,
                    padx=5,
                    pady=5
                )

                entry.insert(0, str(values[j]))

                entries.append(entry)

            self.edge_entries.append(entries)

        # Clear previous output when input fields change
        self.clear_output()

    # ==================================================
    # BUTTONS
    # ==================================================

    def create_buttons(self):

        frame = tk.Frame(
            self.main_frame,
            bg=self.bg
        )

        frame.pack(
            fill="x",
            padx=30,
            pady=15
        )

        self.make_button(
            frame,
            "CHECK BIPARTITE GRAPH",
            self.check_graph,
            self.green
        ).pack(
            side="left",
            padx=5
        )

        self.make_button(
            frame,
            "RESET",
            self.reset,
            "#475569"
        ).pack(
            side="left",
            padx=5
        )

        self.make_button(
            frame,
            "CLEAR OUTPUT",
            self.clear_output,
            "#475569"
        ).pack(
            side="left",
            padx=5
        )

    def make_button(
        self, parent, text, command, color=None
    ):

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

    # ==================================================
    # OUTPUT SECTION
    # ==================================================

    def create_output(self):

        self.output_frame = tk.LabelFrame(
            self.main_frame,
            text=" Bipartite Graph Result ",
            bg=self.panel,
            fg=self.accent,
            font=("Segoe UI", 11, "bold"),
            padx=15,
            pady=15
        )

        self.output_frame.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=10
        )

        # STATUS
        self.status_label = tk.Label(
            self.output_frame,
            text="Waiting for graph input...",
            bg=self.panel,
            fg=self.muted,
            font=("Segoe UI", 15, "bold")
        )

        self.status_label.pack(
            anchor="w",
            pady=10
        )

        # GRAPH VISUALIZATION PANEL
        graph_frame = tk.LabelFrame(
            self.output_frame,
            text=" Graph Visualization ",
            bg=self.panel,
            fg=self.accent,
            font=("Segoe UI", 11, "bold"),
            padx=10,
            pady=10
        )

        graph_frame.pack(
            fill="both",
            expand=True,
            pady=10
        )

        graph_container = tk.Frame(
            graph_frame,
            bg=self.panel
        )

        graph_container.pack(
            fill="both",
            expand=True
        )

        self.graph_canvas = tk.Canvas(
            graph_container,
            bg="#101827",
            height=480,
            highlightthickness=0
        )

        self.graph_vscroll = ttk.Scrollbar(
            graph_container,
            orient="vertical",
            command=self.graph_canvas.yview
        )

        self.graph_hscroll = ttk.Scrollbar(
            graph_container,
            orient="horizontal",
            command=self.graph_canvas.xview
        )

        self.graph_canvas.configure(
            yscrollcommand=self.graph_vscroll.set,
            xscrollcommand=self.graph_hscroll.set
        )

        self.graph_canvas.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        self.graph_vscroll.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        self.graph_hscroll.grid(
            row=1,
            column=0,
            sticky="ew"
        )

        graph_container.grid_rowconfigure(0, weight=1)
        graph_container.grid_columnconfigure(0, weight=1)

        self.graph_canvas.bind(
            "<Configure>",
            self.on_graph_resize
        )

        # GRAPH LEGEND
        legend = tk.Frame(
            graph_frame,
            bg=self.panel
        )

        legend.pack(
            anchor="w",
            pady=10
        )

        tk.Label(
            legend,
            text="● Set V1",
            fg="#38bdf8",
            bg=self.panel,
            font=("Segoe UI", 10, "bold")
        ).pack(
            side="left",
            padx=10
        )

        tk.Label(
            legend,
            text="● Set V2",
            fg="#34d399",
            bg=self.panel,
            font=("Segoe UI", 10, "bold")
        ).pack(
            side="left",
            padx=10
        )

        tk.Label(
            legend,
            text="● Conflict",
            fg="#fb7185",
            bg=self.panel,
            font=("Segoe UI", 10, "bold")
        ).pack(
            side="left",
            padx=10
        )

        # TEXTUAL RESULT
        tk.Label(
            self.output_frame,
            text="Detailed Result",
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI", 12, "bold")
        ).pack(
            anchor="w",
            pady=8
        )

        result_container = tk.Frame(
            self.output_frame,
            bg=self.panel
        )

        result_container.pack(
            fill="both",
            expand=True
        )

        self.result_text = tk.Text(
            result_container,
            height=13,
            bg=self.input_bg,
            fg=self.text,
            insertbackground="white",
            font=("Consolas", 11),
            relief="flat",
            wrap="word"
        )

        result_scroll = ttk.Scrollbar(
            result_container,
            orient="vertical",
            command=self.result_text.yview
        )

        self.result_text.configure(
            yscrollcommand=result_scroll.set
        )

        self.result_text.pack(
            side="left",
            fill="both",
            expand=True
        )

        result_scroll.pack(
            side="right",
            fill="y"
        )

        self.result_text.insert(
            "1.0",
            "Enter the graph details and click CHECK BIPARTITE GRAPH."
        )

    # ==================================================
    # BIPARTITE CHECKING USING BFS
    # ==================================================

    def is_bipartite(self, graph, n):

        # -1 = unvisited
        #  0 = Set V1
        #  1 = Set V2

        color = [-1] * n

        queue = deque()

        # Stores an edge causing a coloring conflict
        conflict = None

        # Check every connected component
        for start in range(n):

            if color[start] != -1:
                continue

            # Start BFS
            color[start] = 0
            queue.append(start)

            while queue:

                u = queue.popleft()

                for v in graph[u]:

                    # Same color on adjacent vertices
                    if color[v] == color[u]:

                        conflict = (u, v)

                        return False, color, conflict

                    # Assign opposite color
                    if color[v] == -1:

                        color[v] = 1 - color[u]

                        queue.append(v)

        return True, color, conflict

    # ==================================================
    # CHECK GRAPH
    # ==================================================

    def check_graph(self):

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
                    "Click Generate Edge Fields after changing "
                    "the number of edges."
                )

        except ValueError as e:

            messagebox.showerror(
                "Input Error",
                str(e)
            )

            return

        # Initialize adjacency list
        graph = [[] for _ in range(n)]

        seen = set()
        duplicates = []
        processed = []

        # Read all edges
        for index, entries in enumerate(self.edge_entries):

            try:

                u = int(entries[0].get())
                v = int(entries[1].get())

                # Validate vertices
                if not (1 <= u <= n and 1 <= v <= n):

                    raise ValueError(
                        f"Edge {index+1}: Vertex must be "
                        f"between 1 and {n}."
                    )

                # Convert to zero-based indexing
                a = u - 1
                b = v - 1

                # Undirected edge key
                key = (min(a, b), max(a, b))

                # Detect duplicate edges
                if key in seen:

                    duplicates.append((u, v))
                    continue

                seen.add(key)

                # Add undirected edge
                graph[a].append(b)

                if a != b:
                    graph[b].append(a)

                processed.append((u, v))

            except ValueError as e:

                messagebox.showerror(
                    "Edge Input Error",
                    str(e)
                )

                return

        # Execute BFS algorithm
        result, color, conflict = self.is_bipartite(
            graph, n
        )

        # Store information for graph visualization
        self.graph_data = {
            "n": n,
            "edges": [
                (u - 1, v - 1)
                for u, v in processed
            ],
            "colors": color,
            "result": result,
            "conflict": conflict
        }

        # Display result and draw graph
        self.display_result(
            result,
            color,
            n,
            processed,
            duplicates,
            conflict
        )

        self.draw_graph()

    # ==================================================
    # GRAPH VISUALIZATION
    # ==================================================

    def on_graph_resize(self, event=None):

        if self.graph_data is not None:
            self.draw_graph()

    def draw_graph(self):

        if self.graph_data is None:
            return

        canvas = self.graph_canvas

        canvas.delete("all")

        n = self.graph_data["n"]
        edges = self.graph_data["edges"]
        colors = self.graph_data["colors"]
        result = self.graph_data["result"]
        conflict = self.graph_data["conflict"]

        # Drawing area
        width = max(canvas.winfo_width(), 600)
        height = max(canvas.winfo_height(), 480)

        # Increase drawing area for larger graphs
        drawing_width = max(width, n * 35 + 200, 900)
        drawing_height = max(height, n * 35 + 200, 650)

        canvas.configure(
            scrollregion=(
                0, 0,
                drawing_width,
                drawing_height
            )
        )

        # Center of graph
        cx = drawing_width / 2
        cy = drawing_height / 2

        # Circular arrangement
        radius = min(
            drawing_width,
            drawing_height
        ) * 0.39

        node_radius = max(
            11,
            min(25, 800 // max(n, 1))
        )

        positions = {}

        # Calculate vertex positions
        for i in range(n):

            angle = (
                2 * math.pi * i / n
                - math.pi / 2
            )

            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)

            positions[i] = (x, y)

        # Draw graph edges
        for u, v in edges:

            x1, y1 = positions[u]
            x2, y2 = positions[v]

            # Highlight conflict edge
            is_conflict = (
                conflict is not None
                and (
                    (u == conflict[0] and v == conflict[1])
                    or
                    (u == conflict[1] and v == conflict[0])
                )
            )

            edge_color = (
                "#fb7185"
                if is_conflict
                else "#94a3b8"
            )

            edge_width = 4 if is_conflict else 2.5

            if u == v:

                # Self-loop
                canvas.create_oval(
                    x1 - 18,
                    y1 - 48,
                    x1 + 18,
                    y1 - 12,
                    outline="#fb7185",
                    width=3
                )

            else:

                canvas.create_line(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill=edge_color,
                    width=edge_width
                )

        # Draw vertices
        for i in range(n):

            x, y = positions[i]

            if result:

                fill_color = (
                    "#38bdf8"
                    if colors[i] == 0
                    else "#34d399"
                )

            else:

                fill_color = "#fb7185"

            canvas.create_oval(
                x - node_radius,
                y - node_radius,
                x + node_radius,
                y + node_radius,
                fill=fill_color,
                outline="white",
                width=2
            )

            canvas.create_text(
                x,
                y,
                text=str(i + 1),
                fill="#101827",
                font=(
                    "Segoe UI",
                    max(8, min(12, node_radius // 2)),
                    "bold"
                )
            )

        # Graph title
        title = (
            "BIPARTITE GRAPH"
            if result
            else "NON-BIPARTITE GRAPH"
        )

        title_color = (
            self.green
            if result
            else self.red
        )

        canvas.create_text(
            cx,
            35,
            text=title,
            fill=title_color,
            font=("Segoe UI", 16, "bold")
        )

        # Conflict information
        if not result and conflict is not None:

            canvas.create_text(
                cx,
                drawing_height - 35,
                text=(
                    f"Color conflict between "
                    f"Vertex {conflict[0]+1} and "
                    f"Vertex {conflict[1]+1}"
                ),
                fill=self.red,
                font=("Segoe UI", 11, "bold")
            )

    # ==================================================
    # DISPLAY RESULTS
    # ==================================================

    def display_result(
        self,
        result,
        color,
        n,
        processed,
        duplicates,
        conflict
    ):

        self.result_text.delete(
            "1.0",
            tk.END
        )

        output = "GRAPH INFORMATION\n"
        output += "=" * 48 + "\n"

        output += f"Number of vertices : {n}\n"
        output += f"Input edges        : {len(processed) + len(duplicates)}\n"
        output += f"Unique edges       : {len(processed)}\n"
        output += f"Repeated edges     : {len(duplicates)}\n\n"

        output += "PROCESSED EDGE LIST\n"
        output += "-" * 48 + "\n"

        for u, v in processed:
            output += f"{u} -- {v}\n"

        if duplicates:

            output += "\nDUPLICATE EDGES IGNORED\n"

            for u, v in duplicates:
                output += f"{u} -- {v}\n"

        output += "\n" + "=" * 48 + "\n\n"

        if result:

            # Generate vertex sets
            v1 = [
                i + 1
                for i in range(n)
                if color[i] == 0
            ]

            v2 = [
                i + 1
                for i in range(n)
                if color[i] == 1
            ]

            self.status_label.config(
                text="BIPARTITE GRAPH",
                fg=self.green
            )

            output += "RESULT: THE GRAPH IS BIPARTITE\n\n"

            output += "SET V1 (BLUE VERTICES)\n"
            output += f"V1 = {v1}\n\n"

            output += "SET V2 (GREEN VERTICES)\n"
            output += f"V2 = {v2}\n\n"

            output += (
                "Every edge connects a vertex in V1 "
                "to a vertex in V2.\n\n"
            )

            output += "Therefore, the graph is bipartite."

        else:

            self.status_label.config(
                text="NOT A BIPARTITE GRAPH",
                fg=self.red
            )

            output += "RESULT: THE GRAPH IS NOT BIPARTITE\n\n"

            if conflict is not None:

                output += (
                    f"Color conflict detected between "
                    f"vertices {conflict[0]+1} and "
                    f"{conflict[1]+1}.\n\n"
                )

            output += (
                "The graph cannot be divided into two "
                "independent vertex sets.\n\n"
            )

            output += (
                "An odd cycle or a self-loop may cause "
                "this conflict."
            )

        self.result_text.insert(
            "1.0",
            output
        )

    # ==================================================
    # CLEAR OUTPUT
    # ==================================================

    def clear_output(self):

        self.status_label.config(
            text="Waiting for graph input...",
            fg=self.muted
        )

        self.result_text.delete(
            "1.0",
            tk.END
        )

        self.result_text.insert(
            "1.0",
            "Enter the graph details and click CHECK BIPARTITE GRAPH."
        )

        self.graph_data = None

        self.graph_canvas.delete("all")

    # ==================================================
    # RESET
    # ==================================================

    def reset(self):

        self.vertices.delete(0, tk.END)
        self.vertices.insert(0, "5")

        self.edge_count.delete(0, tk.END)
        self.edge_count.insert(0, "5")

        self.generate_fields()
        self.clear_output()

        self.main_canvas.yview_moveto(0)


# ======================================================
# MAIN PROGRAM
# ======================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = BipartiteGraphGUI(root)

    root.mainloop()
