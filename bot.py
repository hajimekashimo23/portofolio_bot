# Import required libraries
import discord
from discord.ext import commands
from M3L3logic import DB_Manager  # NOTE: Use M3L3logic
from config import DATABASE, TOKEN  # Configuration file with DB path and bot token

# Set up bot intents (permissions), especially for reading message content
intents = discord.Intents.default()
intents.message_content = True  # Required for reading user input messages

# Initialize the bot with a command prefix and intents
bot = commands.Bot(command_prefix='!', intents=intents)

# Initialize the database manager with the given database
manager = DB_Manager(DATABASE)

# Event triggered when the bot is ready and connected
@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user}')

# Command: !start
# Sends an introduction message and lists the available commands
@bot.command(name='start')
async def start_command(ctx):
    await ctx.send("Halo! Saya adalah bot manajer proyek\nSaya akan membantu kamu menyimpan proyek dan informasi tentangnya!)")
    await info(ctx)  # Show command list

# Command: !info
# Displays a list of available bot commands and how to use them
@bot.command(name='info')
async def info(ctx):
    await ctx.send("""
Berikut adalah perintah yang dapat membantu kamu:

!new_project - gunakan untuk menambahkan proyek baru
!projects - gunakan untuk menampilkan semua proyek
!update_projects - gunakan untuk mengubah data proyek
!skills - gunakan untuk menghubungkan keterampilan ke proyek
!delete - gunakan untuk menghapus proyek

Kamu juga dapat memasukkan nama proyek untuk mengetahui informasi tentangnya!""")

# Command: !new_project
# Interactively collects project information from the user and saves it to the database
@bot.command(name='new_project')
async def new_project(ctx):
    await ctx.send("Masukkan nama proyek:")

    # Check function to ensure input is from the same user and channel
    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel

    # Get project name
    name = await bot.wait_for('message', check=check)
    data = [ctx.author.id, name.content]

    # Get project link
    await ctx.send("Masukkan link proyek")
    link = await bot.wait_for('message', check=check)
    data.append(link.content)

    # Get list of possible statuses
    statuses = [x[0] for x in manager.get_statuses()]
    await ctx.send("Masukkan status proyek saat ini", delete_after=60.0)
    await ctx.send("\n".join(statuses), delete_after=60.0)

    # Get status from user
    status = await bot.wait_for('message', check=check)
    if status.content not in statuses:
        await ctx.send("Kamu memilih status yang tidak ada dalam daftar, silakan coba lagi!)", delete_after=60.0)
        return

    # Save project with selected status
    status_id = manager.get_status_id(status.content)
    data.append(status_id)
    manager.insert_project([tuple(data)])
    await ctx.send("Proyek telah disimpan")

# Command: !projects
# Fetch and display all projects associated with the user
@bot.command(name='projects')
async def get_projects(ctx):
    user_id = ctx.author.id
    projects = manager.get_projects(user_id)
    if projects:
        # Display each project's name and link
        text = "\n".join([f"Project name: {x[2]} \nLink: {x[4]}\n" for x in projects])
        await ctx.send(text)
    else:
        await ctx.send('Kamu belum memiliki proyek!\nKamu dapat menambahkannya menggunakan perintah !new_project')

# Command: !skills
# Allows user to link a skill to one of their projects
@bot.command(name='skills')
async def skills(ctx):
    user_id = ctx.author.id
    projects = manager.get_projects(user_id)

    if projects:
        # Get list of project names for the user
        projects = [x[2] for x in projects]
        await ctx.send('Pilih proyek yang ingin kamu tambahkan keterampilan')
        await ctx.send("\n".join(projects))

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        # Choose project
        project_name = await bot.wait_for('message', check=check)
        if project_name.content not in projects:
            await ctx.send('Kamu tidak memiliki proyek tersebut, silakan coba lagi!)')
            return

        # Choose skill
        skills = [x[1] for x in manager.get_skills()]
        await ctx.send('Pilih keterampilan')
        await ctx.send("\n".join(skills))

        skill = await bot.wait_for('message', check=check)
        if skill.content not in skills:
            await ctx.send('Sepertinya kamu memilih keterampilan yang tidak ada dalam daftar, silakan coba lagi!)')
            return

        # Save the selected skill for the project
        manager.insert_skill(user_id, project_name.content, skill.content)
        await ctx.send(f'Keterampilan {skill.content} telah ditambahkan ke proyek {project_name.content}')
    else:
        await ctx.send('Kamu belum memiliki proyek!\nKamu dapat menambahkannya menggunakan perintah !new_project')

# Command: !delete
# Allows user to delete one of their projects
@bot.command(name='delete')
async def delete_project(ctx):
    user_id = ctx.author.id
    projects = manager.get_projects(user_id)

    if projects:
        projects = [x[2] for x in projects]
        await ctx.send("Pilih proyek yang ingin kamu hapus")
        await ctx.send("\n".join(projects))

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        project_name = await bot.wait_for('message', check=check)
        if project_name.content not in projects:
            await ctx.send('Kamu tidak memiliki proyek tersebut, silakan coba lagi!')
            return

        # Delete the selected project
        project_id = manager.get_project_id(project_name.content, user_id)
        manager.delete_project(user_id, project_id)
        await ctx.send(f'Proyek {project_name.content} telah dihapus!')
    else:
        await ctx.send('Kamu belum memiliki proyek!\nKamu dapat menambahkannya menggunakan perintah !new_project')

# Command: !update_projects
# Allows user to update specific information for a selected project
@bot.command(name='update_projects')
async def update_projects(ctx):
    user_id = ctx.author.id
    projects = manager.get_projects(user_id)

    if projects:
        projects = [x[2] for x in projects]
        await ctx.send("Pilih proyek yang ingin kamu ubah")
        await ctx.send("\n".join(projects))

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        project_name = await bot.wait_for('message', check=check)
        if project_name.content not in projects:
            await ctx.send("Ada yang salah! Silakan pilih proyek yang ingin kamu ubah lagi:")
            return

        # Let user choose which attribute to update
        await ctx.send("Pilih apa yang ingin kamu ubah dalam proyek")
        attributes = {'Nama proyek': 'project_name', 'Deskripsi': 'description', 'Link': 'url', 'Status': 'status_id'}
        await ctx.send("\n".join(attributes.keys()))

        attribute = await bot.wait_for('message', check=check)
        if attribute.content not in attributes:
            await ctx.send("Sepertinya kamu membuat kesalahan, silakan coba lagi!")
            return

        # Handle status separately (convert name to ID)
        if attribute.content == 'Status':
            statuses = manager.get_statuses()
            await ctx.send("Pilih status baru untuk proyek")
            await ctx.send("\n".join([x[0] for x in statuses]))
            update_info = await bot.wait_for('message', check=check)
            if update_info.content not in [x[0] for x in statuses]:
                await ctx.send("Status yang dipilih tidak valid, silakan coba lagi!")
                return
            update_info = manager.get_status_id(update_info.content)
        else:
            # Get new value for other attributes
            await ctx.send(f"Masukkan nilai baru untuk {attribute.content}")
            update_info = await bot.wait_for('message', check=check)
            update_info = update_info.content

        # Update the project in the database
        manager.update_projects(attributes[attribute.content], (update_info, project_name.content, user_id))
        await ctx.send("Selesai! Pembaruan telah dilakukan!")
    else:
        await ctx.send('Kamu belum memiliki proyek!\nKamu dapat menambahkannya menggunakan perintah !new_project')

# Run the bot with the token from the config
bot.run(TOKEN)
