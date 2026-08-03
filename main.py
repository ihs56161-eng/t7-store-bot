import os
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# قاموس لتخزين الشخص اللي استلم التذكرة لكل روم (channel_id: staff_member_id)
claimed_tickets = {}

# أزرار التذاكر (تتضمن قفل، استلام، إلغاء الاستلام، واستدعاء)
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="قفل التذكرة", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("جاري قفل التذكرة وحذف الروم...", ephemeral=True)
        await interaction.channel.delete()

    @discord.ui.button(label="استلام التذكرة", style=discord.ButtonStyle.success, emoji="🙋‍♂️", custom_id="claim_ticket")
    async def claim_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        claimed_tickets[interaction.channel.id] = interaction.user.id
        await interaction.response.send_message(f"✅ تم استلام التذكرة بواسطة: {interaction.user.mention}")

    @discord.ui.button(label="إلغاء الاستلام", style=discord.ButtonStyle.secondary, emoji="↩️", custom_id="unclaim_ticket")
    async def unclaim_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.channel.id in claimed_tickets:
            del claimed_tickets[interaction.channel.id]
            await interaction.response.send_message(f"🔄 تم إلغاء استلام التذكرة بواسطة: {interaction.user.mention}")
        else:
            await interaction.response.send_message("⚠️ هذه التذكرة لم يتم استلامها أساساً!", ephemeral=True)

    @discord.ui.button(label="استدعاء المسؤول", style=discord.ButtonStyle.primary, emoji="🔔", custom_id="call_staff")
    async def call_staff(self, interaction: discord.Interaction, button: discord.ui.Button):
        staff_id = claimed_tickets.get(interaction.channel.id)
        if staff_id:
            staff_member = interaction.guild.get_member(staff_id)
            if staff_member:
                await interaction.response.send_message(f"🔔 تم استدعاؤك يا {staff_member.mention}! صاحب التذكرة يناديك هنا.")
            else:
                await interaction.response.send_message("⚠️ المسؤول الذي استلم التذكرة غير موجود حالياً في السيرفر.", ephemeral=True)
        else:
            await interaction.response.send_message("⚠️ لم يتم استلام هذه التذكرة من قبل أي مسؤول حتى يتم استدعاؤه!", ephemeral=True)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")


# أمر بسيط لإرسال أزرار التذاكر في أي روم تجربه
@bot.command()
@commands.has_permissions(administrator=True)
async def panel(ctx):
    embed = discord.Embed(
        title="🎫 نظام تذاكر متجر T7",
        description="اضغط على الأزرار أدناه للتحكم بالتذكرة:",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed, view=TicketView())


TOKEN = os.getenv("TOKEN")
if TOKEN:
    bot.run(TOKEN)
else:
    print("Error: TOKEN environment variable not found!")
    
