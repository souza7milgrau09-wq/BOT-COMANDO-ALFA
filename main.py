import discord
from discord.ext import commands
import json
import random
from datetime import datetime, timedelta

import os
TOKEN=os.getenv("MTQ4NTI4NTIzODczMTk2NDQ4Ng.G8qITQ.mmR-qUvltKDweUv1PuxY-AllO_bGgPazkYCsBM")
DONO_ID = 1349812947160924253

intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ================= CHECK DONO =================
def dono_only():
    async def predicate(ctx):
        return ctx.author.id == DONO_ID
    return commands.check(predicate)

# ================= DATA =================
def load_data():
    try:
        with open("data.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open("data.json", "w") as f:
        json.dump(data, f, indent=4)

# ================= EVENTOS =================
@bot.event
async def on_ready():
    bot.add_view(VerificarView())
    print(f"🔥 {bot.user} ONLINE")

@bot.event
async def on_member_join(member):
    data = load_data()
    gid = str(member.guild.id)

    role = discord.utils.get(member.guild.roles, name="👥 Convidado")
    if role:
        await member.add_roles(role)

    if gid in data and "welcome" in data[gid]:
        canal = bot.get_channel(data[gid]["welcome"])
        if canal:
            await canal.send(
                f"👋 Bem-vindo {member.mention}!\n"
                f"➡️ Vá até o canal #✅・verificação para liberar acesso!"
            )

# ================= ANTI-SPAM + XP =================
spam_control = {}
xp_cooldown = {}

@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    gid = str(message.guild.id)
    uid = str(message.author.id)
    now = datetime.now()

    if uid not in spam_control:
        spam_control[uid] = []

    spam_control[uid].append(now)
    spam_control[uid] = [t for t in spam_control[uid] if now - t < timedelta(seconds=5)]

    if len(spam_control[uid]) > 6:
        return

    if uid in xp_cooldown and now < xp_cooldown[uid]:
        await bot.process_commands(message)
        return

    xp_cooldown[uid] = now + timedelta(seconds=10)

    data = load_data()

    if gid not in data:
        data[gid] = {}

    if "users" not in data[gid]:
        data[gid]["users"] = {}

    if uid not in data[gid]["users"]:
        data[gid]["users"][uid] = {"xp": 0, "level": 1, "money": 0}

    user = data[gid]["users"][uid]

    user["xp"] += random.randint(5, 15)

    if user["xp"] >= user["level"] * 100:
        user["xp"] = 0
        user["level"] += 1
        await message.channel.send(f"🎉 {message.author.mention} subiu para nível {user['level']}!")

    user["money"] += random.randint(1, 3)

    save_data(data)

    await bot.process_commands(message)

# ================= VERIFICAÇÃO =================
class VerificarView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="✅ Verificar", style=discord.ButtonStyle.green, custom_id="botao_verificar")
    async def verificar(self, interaction: discord.Interaction, button: discord.ui.Button):
        membro = interaction.user

        role_membro = discord.utils.get(membro.guild.roles, name="👤 Membro")
        role_convidado = discord.utils.get(membro.guild.roles, name="👥 Convidado")

        if role_membro:
            await membro.add_roles(role_membro)

        if role_convidado:
            await membro.remove_roles(role_convidado)

        await interaction.response.send_message("✅ Você foi verificado!", ephemeral=True)

@bot.command()
@dono_only()
async def verificação(ctx):
    embed = discord.Embed(
        title="🔐 Sistema de Verificação",
        description="Clique abaixo para liberar acesso.",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed, view=VerificarView())

# ================= LOCK =================
@bot.command()
async def lock(ctx):
    cargos = ["👑 Dono", "🧬 Co-Dono"]

    if not any(role.name in cargos for role in ctx.author.roles):
        return await ctx.send("❌ Sem permissão")

    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = False
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)

    await ctx.send("🔒 Canal trancado!")

@bot.command()
async def unlock(ctx):
    cargos = ["👑 Dono", "🧬 Co-Dono"]

    if not any(role.name in cargos for role in ctx.author.roles):
        return await ctx.send("❌ Sem permissão")

    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = None
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)

    await ctx.send("🔓 Canal destrancado!")

# ================= LIMPAR PRO =================
@bot.command()
async def limpar(ctx, tipo=None, quantidade: int = None):
    cargos_permitidos = ["👑 Dono", "🧬 Co-Dono", "🛡️ Admin"]

    if not any(role.name in cargos_permitidos for role in ctx.author.roles):
        return await ctx.send("❌ Sem permissão")

    if tipo is None:
        return await ctx.send("❌ Use corretamente")

    if tipo.isdigit():
        qtd = int(tipo)
        await ctx.channel.purge(limit=qtd + 1)
        return

# ================= TEXT =================
@bot.command()
async def text(ctx, cor=None, *, mensagem=None):
    cargos = ["👑 Dono", "🧬 Co-Dono"]

    if not any(role.name in cargos for role in ctx.author.roles):
        return await ctx.send("❌ Sem permissão")

    await ctx.message.delete()

    embed = discord.Embed(description=f"**{mensagem}**", color=0x000000)
    await ctx.send(embed=embed)

# ================= CONFIG =================
@bot.command()
@dono_only()
async def setwelcome(ctx, canal: discord.TextChannel):
    data = load_data()
    gid = str(ctx.guild.id)

    if gid not in data:
        data[gid] = {}

    data[gid]["welcome"] = canal.id
    save_data(data)

    await ctx.send("✅ Canal definido")

# ================= PING =================
@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 {round(bot.latency * 1000)}ms")

# ================= ERROS =================
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    print(error)

bot.run(TOKEN)
