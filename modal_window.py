import discord
from discord.ext import commands
from discord import ui, ButtonStyle, TextStyle

# Mendefinisikan jendela modal
class TestModal(ui.Modal, title='Judul Test'):
    # Mendefinisikan kolom teks di jendela modal
    field_1 = ui.TextInput(label='Teks Pendek')
    field_2 = ui.TextInput(label='Teks Panjang', style=TextStyle.paragraph)

    # Metode yang dipanggil saat modal dikirim
    async def on_submit(self, interaction: discord.Interaction):
        # Memperbarui pesan dengan data yang dimasukkan
        await interaction.message.edit(content=f'Teks Pendek: {self.field_1.value}\n'
                                             f'Teks Panjang: {self.field_2.value}')
        # Memeriksa apakah respons sudah dikirim
        if not interaction.response.is_done():
            # Menunda pengiriman respons
            await interaction.response.defer()

# Mendefinisikan tombol
class TestButton(ui.Button):
    # Inisialisasi tombol dengan properti yang ditentukan
    def __init__(self, label="Tombol Test", style=ButtonStyle.blurple, row=0):
        super().__init__(label=label, style=style, row=row)

    # Metode yang dipanggil saat tombol ditekan
    async def callback(self, interaction: discord.Interaction):
        # Mengirim pesan pribadi ke pengguna
        await interaction.user.send("Kamu telah menekan tombol")
        # Mengirim pesan ke channel tempat tombol ditekan
        await interaction.message.channel.send("Kamu telah menekan tombol")
        # Membuka jendela modal
        await interaction.response.send_modal(TestModal())
        # Mengubah warna tombol setelah ditekan
        self.style = ButtonStyle.gray

        # Memeriksa apakah respons sudah dikirim
        if not interaction.response.is_done():
            # Menunda pengiriman respons
            await interaction.response.defer()

# Mendefinisikan tampilan dengan tombol
class TestView(ui.View):
    # Inisialisasi tampilan
    def __init__(self):
        super().__init__()
        # Menambahkan tombol ke tampilan
        self.add_item(TestButton(label="Tombol Test"))

# Pengaturan bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Event saat bot siap
@bot.event
async def on_ready():
    # Menampilkan pesan saat berhasil login
    print(f'Berhasil login sebagai {bot.user}')

# Perintah untuk menampilkan tombol
@bot.command()
async def test(ctx):
    # Mengirim pesan dengan tampilan yang berisi tombol
    await ctx.send("Tekan tombol di bawah ini:", view=TestView())

# Menjalankan bot dengan token
bot.run('Your Token Here')