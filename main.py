import customtkinter

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

root = customtkinter.CTk()
root.geometry("800x600")
frame = customtkinter.CTkFrame(root)
frame.pack(pady=20, padx=60, fill='both', expand=True)
label = customtkinter.CTkLabel(master=frame, text="Lorem ipsum", font=("Roboto", 24))
label.pack(pady=12, padx=10)

count = 0
def simulate():
    global count
    print(f"mantap {count}")
    label.configure(text=f"mantap {count}")
    label.pack()
    count+=1
    root.after(500, simulate)

root.after(500, simulate)

root.mainloop()