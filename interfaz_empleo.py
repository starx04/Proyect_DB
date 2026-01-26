import customtkinter as ctk
import psycopg
from psycopg import Error
from tkinter import messagebox, ttk

# CONFIGURACIÓN DE APARIENCIA
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class AppBolsaEmpleo(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Job Connect - Gestión Completa de Candidatos")
        self.geometry("1300x850")

        # --- CONEXIÓN A LA BASE DE DATOS (Sincronizada con Django) ---
        self.db_params = {
            "host": "localhost",
            "port": "5432",
            "user": "openpg",
            "password": "openpgpwd",
            "database": "db_bolsa_empleo_app"
        }

        self.selected_user_id = None  # Almacena el ID del usuario seleccionado para Modificar/Eliminar

        # Layout Principal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.logo = ctk.CTkLabel(self.sidebar, text="JOB CONNECT", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=30)

        # Contenedor principal
        self.main_view = ctk.CTkScrollableFrame(self, corner_radius=15)
        self.main_view.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.init_ui()

    def get_connection(self):
        return psycopg.connect(**self.db_params)

    def init_ui(self):
        # Título
        ctk.CTkLabel(self.main_view, text="PERFIL DEL CANDIDATO", font=("Roboto", 22, "bold")).pack(pady=10)

        # --- GRID PARA CAMPOS (2 columnas) ---
        form_container = ctk.CTkFrame(self.main_view, fg_color="transparent")
        form_container.pack(fill="x", padx=10)
        form_container.grid_columnconfigure((0, 1), weight=1)

        # Columna 1
        self.entry_nombre = self.add_field(form_container, "Nombre Completo:", 0, 0)
        self.entry_email = self.add_field(form_container, "Email:", 1, 0)
        self.entry_pass = self.add_field(form_container, "Password:", 2, 0, show="*")
        self.entry_dni = self.add_field(form_container, "N° Identificación (DNI/Cédula):", 3, 0)
        self.entry_nacimiento = self.add_field(form_container, "F. Nacimiento (YYYY-MM-DD):", 4, 0)
        
        # Columna 2
        self.combo_genero = self.add_combo(form_container, "Género:", ["masculino", "femenino", "otro", "prefiero_no_decir"], 0, 1)
        self.entry_titulo = self.add_field(form_container, "Título Profesional:", 1, 1)
        self.entry_telefono = self.add_field(form_container, "Teléfono:", 2, 1)
        self.entry_salario = self.add_field(form_container, "Salario Esperado:", 3, 1)
        self.entry_dispo = self.add_field(form_container, "Disponibilidad (Ej: Inmediata):", 4, 1)

        # URLs (Fila completa)
        self.entry_linkedin = self.add_field(form_container, "LinkedIn URL:", 5, 0)
        self.entry_github = self.add_field(form_container, "GitHub URL:", 5, 1)
        
        # --- BOTONES DE ACCIÓN ---
        btn_frame = ctk.CTkFrame(self.main_view, fg_color="transparent")
        btn_frame.pack(pady=20)

        ctk.CTkButton(btn_frame, text="AGREGAR", fg_color="#28a745", command=self.create_record).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="MODIFICAR", fg_color="#ffc107", text_color="black", command=self.update_record).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="ELIMINAR", fg_color="#dc3545", command=self.delete_record).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="LIMPIAR", fg_color="#6c757d", command=self.clear_form).pack(side="left", padx=10)

        # --- TABLA (TREEVIEW) ---
        self.setup_table()

    def add_field(self, master, text, row, col, **kwargs):
        ctk.CTkLabel(master, text=text).grid(row=row*2, column=col, sticky="w", padx=15, pady=(5,0))
        entry = ctk.CTkEntry(master, width=350, **kwargs)
        entry.grid(row=row*2+1, column=col, padx=15, pady=(0,10))
        return entry

    def add_combo(self, master, text, values, row, col):
        ctk.CTkLabel(master, text=text).grid(row=row*2, column=col, sticky="w", padx=15, pady=(5,0))
        combo = ctk.CTkComboBox(master, values=values, width=350)
        combo.grid(row=row*2+1, column=col, padx=15, pady=(0,10))
        return combo

    def setup_table(self):
        table_frame = ctk.CTkFrame(self.main_view)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Configuración de estilo
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b", rowheight=25)
        style.map("Treeview", background=[('selected', '#1a73e8')])

        self.tree = ttk.Treeview(table_frame, columns=("ID", "Nombre", "DNI", "Título", "Email"), show='headings')
        self.tree.heading("ID", text="ID"); self.tree.column("ID", width=40)
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("DNI", text="Identificación")
        self.tree.heading("Título", text="Título")
        self.tree.heading("Email", text="Email")
        
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_item_select)
        self.refresh_table()

    # --- LÓGICA CRUD ---

    def refresh_table(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT u.id, c.nombre_completo, c.numero_identificacion, c.titulo_profesional, u.email 
                FROM accounts_usuario u JOIN accounts_candidato c ON u.id = c.usuario_id
            """)
            for row in cur.fetchall(): self.tree.insert("", "end", values=row)
            conn.close()
        except Exception as e: print(f"Error: {e}")

    def on_item_select(self, event):
        selected = self.tree.focus()
        if not selected: return
        data = self.tree.item(selected, 'values')
        self.selected_user_id = data[0]

        # Cargar datos detallados de la BD
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT c.nombre_completo, u.email, c.numero_identificacion, c.fecha_nacimiento, 
                       c.genero, c.titulo_profesional, c.telefono, c.salario_esperado, 
                       c.disponibilidad, c.linkedin_url, c.github_url
                FROM accounts_usuario u JOIN accounts_candidato c ON u.id = c.usuario_id WHERE u.id = %s
            """, (self.selected_user_id,))
            res = cur.fetchone()
            
            self.clear_form(keep_id=True)
            self.entry_nombre.insert(0, res[0])
            self.entry_email.insert(0, res[1])
            self.entry_dni.insert(0, res[2])
            self.entry_nacimiento.insert(0, res[3])
            self.combo_genero.set(res[4])
            self.entry_titulo.insert(0, res[5])
            self.entry_telefono.insert(0, res[6] or "")
            self.entry_salario.insert(0, res[7] or "")
            self.entry_dispo.insert(0, res[8] or "")
            self.entry_linkedin.insert(0, res[9] or "")
            self.entry_github.insert(0, res[10] or "")
            conn.close()
        except Exception as e: print(e)

    def create_record(self):
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO accounts_usuario (email, username, password, tipo_usuario, is_active, is_staff, is_superuser, date_joined) 
                VALUES (%s, %s, %s, 'candidato', true, false, false, NOW()) RETURNING id
            """, (self.entry_email.get(), self.entry_email.get(), self.entry_pass.get()))
            uid = cur.fetchone()[0]
            
            cur.execute("""
                INSERT INTO accounts_candidato (usuario_id, nombre_completo, numero_identificacion, fecha_nacimiento, 
                genero, titulo_profesional, telefono, salario_esperado, disponibilidad, linkedin_url, github_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (uid, self.entry_nombre.get(), self.entry_dni.get(), self.entry_nacimiento.get(), 
                  self.combo_genero.get(), self.entry_titulo.get(), self.entry_telefono.get(), 
                  self.entry_salario.get() or None, self.entry_dispo.get(), self.entry_linkedin.get(), self.entry_github.get()))
            
            conn.commit()
            messagebox.showinfo("Éxito", "Candidato registrado")
            self.refresh_table()
            self.clear_form()
        except Exception as e: messagebox.showerror("Error", f"No se pudo guardar: {e}")

    def update_record(self):
        if not self.selected_user_id:
            messagebox.showwarning("Error", "Selecciona un registro de la tabla")
            return
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute("UPDATE accounts_usuario SET email=%s, username=%s WHERE id=%s", 
                        (self.entry_email.get(), self.entry_email.get(), self.selected_user_id))
            cur.execute("""
                UPDATE accounts_candidato SET nombre_completo=%s, numero_identificacion=%s, fecha_nacimiento=%s, 
                genero=%s, titulo_profesional=%s, telefono=%s, salario_esperado=%s, disponibilidad=%s, 
                linkedin_url=%s, github_url=%s WHERE usuario_id=%s
            """, (self.entry_nombre.get(), self.entry_dni.get(), self.entry_nacimiento.get(), 
                  self.combo_genero.get(), self.entry_titulo.get(), self.entry_telefono.get(), 
                  self.entry_salario.get() or None, self.entry_dispo.get(), 
                  self.entry_linkedin.get(), self.entry_github.get(), self.selected_user_id))
            conn.commit()
            messagebox.showinfo("Éxito", "Registro actualizado")
            self.refresh_table()
        except Exception as e: messagebox.showerror("Error", str(e))

    def delete_record(self):
        if not self.selected_user_id: return
        if messagebox.askyesno("Confirmar", "¿Desea eliminar permanentemente este perfil?"):
            try:
                conn = self.get_connection()
                cur = conn.cursor()
                cur.execute("DELETE FROM accounts_candidato WHERE usuario_id=%s", (self.selected_user_id,))
                cur.execute("DELETE FROM accounts_usuario WHERE id=%s", (self.selected_user_id,))
                conn.commit()
                self.refresh_table()
                self.clear_form()
            except Exception as e: messagebox.showerror("Error", str(e))

    def clear_form(self, keep_id=False):
        if not keep_id: self.selected_user_id = None
        for entry in [self.entry_nombre, self.entry_email, self.entry_pass, self.entry_dni, 
                      self.entry_nacimiento, self.entry_titulo, self.entry_telefono, 
                      self.entry_salario, self.entry_dispo, self.entry_linkedin, self.entry_github]:
            entry.delete(0, 'end')

if __name__ == "__main__":
    app = AppBolsaEmpleo()
    app.mainloop()