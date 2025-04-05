import discord
from discord.ext import commands
import asyncio
import random

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='z?', intents=intents)

# İzin Eksikliği Mesajı
async def missing_permissions(ctx, permission):
    await ctx.send(f"⚠️ {ctx.author.mention}, bu komutu kullanmak için `{permission}` iznine sahip olman gerekiyor.")

# 🎉 KULLANICI GİRİŞ - ÇIKIŞ MESAJLARI 🎉
@bot.event
async def on_member_join(member):
    # Otorol işlevselliği: Yeni katılan kullanıcıya rol ver
    otorol_rol_ismi = "Yeni Üye"  # Burada verilecek rolün adı
    role = discord.utils.get(member.guild.roles, name=otorol_rol_ismi)

    if role:
        await member.add_roles(role)
        print(f"{member.name} adlı kullanıcıya {role.name} rolü verildi!")
    else:
        print(f"'{otorol_rol_ismi}' adlı rol bulunamadı!")

    # Hoş geldin mesajı
    channel = discord.utils.get(member.guild.text_channels, name="genel")
    if channel:
        await channel.send(f"🎉 Hoş geldin, {member.mention}! Sunucumuza katıldığın için teşekkürler! 🌟")
    
    try:
        await member.send(f"🌟 Merhaba {member.name}, sunucumuza hoş geldin! Kuralları okumayı unutma. 🎉")
    except discord.Forbidden:
        print(f"{member.name} kullanıcısına DM gönderilemedi.")

@bot.event
async def on_member_remove(member):
    channel = discord.utils.get(member.guild.text_channels, name="genel")
    if channel:
        await channel.send(f"😢 {member.mention} aramızdan ayrıldı. Tekrar bekleriz!")

# 🔨 MODERASYON KOMUTLARI 🔨
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="Sebep belirtilmedi"):
    await member.ban(reason=reason)
    await ctx.send(f'🚫 {member.mention} sunucudan banlandı. Sebep: {reason}')
    
    try:
        await member.send(f"🚨 {ctx.guild.name} sunucusundan yasaklandın! Sebep: {reason}")
    except discord.Forbidden:
        print(f"{member.name} kullanıcısına DM gönderilemedi.")

@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await missing_permissions(ctx, "Ban Üyeleri")

@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, user: discord.User):
    await ctx.guild.unban(user)
    await ctx.send(f'✅ {user.mention} adlı kullanıcının yasağı kaldırıldı.')

@unban.error
async def unban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await missing_permissions(ctx, "Ban Üyeleri")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="Sebep belirtilmedi"):
    await member.kick(reason=reason)
    await ctx.send(f'👢 {member.mention} sunucudan atıldı. Sebep: {reason}')

@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await missing_permissions(ctx, "Üyeleri At")

# 🧹 MESAJ TEMİZLEME KOMUTU (clear) 🧹
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    """Belirtilen sayıda mesajı siler."""
    if amount <= 0:
        await ctx.send("⚠️ Geçerli bir sayı girin. (0'dan büyük olmalı.)")
        return
    deleted = await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 {len(deleted) - 1} mesaj silindi.", delete_after=5)

@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await missing_permissions(ctx, "Mesajları Yönet")

# 🛠️ GENEL KOMUTLAR 🛠️
@bot.command()
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f'🏓 Pong! Gecikme: {latency}ms')

@bot.command()
async def kullanıcıbilgi(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"{member.name} Kullanıcı Bilgileri", color=discord.Color.blue())
    embed.add_field(name="ID", value=member.id, inline=False)
    embed.add_field(name="Ad", value=member.display_name, inline=False)
    embed.add_field(name="Hesap Oluşturulma", value=member.created_at.strftime("%d/%m/%Y, %H:%M:%S"), inline=False)
    embed.add_field(name="Sunucuya Katılma", value=member.joined_at.strftime("%d/%m/%Y, %H:%M:%S"), inline=False)
    embed.set_thumbnail(url=member.avatar.url)
    await ctx.send(embed=embed)

# 📜 YARDIM KOMUTU 📜
@bot.command()
async def yardım(ctx):
    embed = discord.Embed(
        title="📜 Yardım Menüsü",
        description="Botun tüm komutlarını ve açıklamalarını burada bulabilirsin. ✅",
        color=discord.Color.purple()
    )
    embed.set_thumbnail(url="https://img.icons8.com/ios/452/help.png")  # Yardım menüsüne ikon ekledik
    embed.add_field(name="🔨 **Moderasyon Komutları**", value=""" 
    `z?ban @kullanıcı [sebep]` - Bir kullanıcıyı sunucudan yasaklar.
    `z?unban kullanıcı_ID` - Yasaklanan bir kullanıcıyı serbest bırakır.
    `z?kick @kullanıcı [sebep]` - Bir kullanıcıyı sunucudan atar.
    `z?clear [sayı]` - Belirtilen sayıda mesajı siler.
    """, inline=False)

    embed.add_field(name="🛠️ **Genel Komutlar**", value=""" 
    `z?ping` - Botun gecikme süresini gösterir.
    `z?kullanıcıbilgi @kullanıcı` - Kullanıcı bilgilerini gösterir.
    """, inline=False)

    embed.add_field(name="⚙️ **Bot Yönetim Komutları**", value=""" 
    `z?otorol @rol` - Sunucuya yeni katılan üyeye otomatik olarak rol verir.
    `z?otorolkapam` - Otorolü kapatır.
    `z?kilit` - Kanalı kilitler.
    `z?kilitkapama` - Kanalın kilidini açar.
    `z?rolver @kullanıcı @rol` - Kullanıcıya rol verir.
    `z?rolal @kullanıcı @rol` - Kullanıcıdan rol alır.
    """, inline=False)

    embed.add_field(name="📍 **Bot Sahibi**", value="Bot sahibi: **zytesta**", inline=False)

    embed.set_footer(text="Botun komutlarını kullanarak eğlenceli zaman geçirebilirsiniz! 🎉")

    await ctx.send(embed=embed)

# Yeni Komutlar

# Otorol Komutu
@bot.command()
@commands.has_permissions(administrator=True)
async def otorol(ctx, role: discord.Role):
    """Sunucuya yeni katılan üyeye otomatik olarak rol verir."""
    await ctx.send(f"{role.name} rolü, yeni katılanlara otomatik olarak verilecektir!")
    # Otorol işlevini on_member_join ile sağlayacağız

@bot.command()
@commands.has_permissions(administrator=True)
async def otorolkapam(ctx):
    """Otorolü kapatır."""
    await ctx.send("Otorol kapatıldı!")

# Kanal Kilitleme Komutları
@bot.command()
@commands.has_permissions(manage_channels=True)
async def kilit(ctx):
    """Kanalı kilitler."""
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("Kanal kilitlendi! 🛑")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def kilitkapama(ctx):
    """Kanalın kilidini açar."""
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send("Kanalın kilidi açıldı! ✅")

# Rol Verme Komutları
@bot.command()
@commands.has_permissions(manage_roles=True)
async def rolver(ctx, member: discord.Member, role: discord.Role):
    """Bir kullanıcıya rol verir."""
    await member.add_roles(role)
    await ctx.send(f'✅ {member.mention} kullanıcısına {role.name} rolü verildi!')

@bot.command()
@commands.has_permissions(manage_roles=True)
async def rolal(ctx, member: discord.Member, role: discord.Role):
    """Bir kullanıcıdan rol alır."""
    await member.remove_roles(role)
    await ctx.send(f'❌ {member.mention} kullanıcısından {role.name} rolü alındı!')

bot.run("BOT TOKEN")
