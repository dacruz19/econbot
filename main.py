import discord
from discord import app_commands
from discord.ext import commands
from auth import token
import time
import json
import random

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='.', intents=intents)

global bets 
bets = {}


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    synced = await bot.tree.sync()
    print(f'Synced {len(synced)} commands.')
    await bot.change_presence(activity=discord.activity.Game("Economy.io"))

class Dbutton(discord.ui.Button):
    def __init__(self,parent_view):
        super().__init__(label='Claim', style=discord.ButtonStyle.green,)
        self.parent_view = parent_view

    async def callback(self, interaction:discord.Interaction):
        user = interaction.user
        
        with open('data.json', 'r') as file:
            data = json.load(file)
            if str(user.id) in data['Accounts']:
                data['Accounts'][str(user.id)][0]['Balance'] += current_drop
                self.disabled = True
                await interaction.response.edit_message(view=self.parent_view)
                await interaction.channel.send(f"{user.mention} has claimed the drop.")

                with open('data.json', 'w') as file:
                    json.dump(data, file)
            else:
                await interaction.response.send_message(f"{interaction.user.mention} must open an account first.")
        
        return

class DView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(Dbutton(self))

@bot.tree.command(name='daily_reward', description="Claim your daily reward 🎁")
async def claim(interaction:discord.Interaction):
    userId = interaction.user.id
    current_time = time.time()
    
    with open('data.json', 'r') as file:
        data = json.load(file)
        if str(userId) in data['Accounts']:
            
            last_claim_time = data['Accounts'][str(userId)][1]['last_claimed']

            if last_claim_time == 0:
                data['Accounts'][str(userId)][1]['last_claimed'] = int(current_time)
                data['Accounts'][str(userId)][0]['Balance'] += 500
                await interaction.response.send_message(f"+$500 You have successfully claimed your daily reward! ", ephemeral= True)
                with open('data.json', 'w') as file:
                    json.dump(data, file)
                return
            
            time_diff = int(current_time) - last_claim_time

            if time_diff >= 86400:
                data['Accounts'][str(userId)][1]['last_claimed'] = int(current_time)
                data['Accounts'][str(userId)][0]['Balance'] += 500
                await interaction.response.send_message(f"+$500 You have successfully claimed your daily reward!", ephemeral= True)
                with open('data.json', 'w') as file:
                    json.dump(data, file)
                return
            else:
                await interaction.response.send_message(f"You have {int((86400 - time_diff)//3600)} hours left and {int(((86400-time_diff)%3600) // 60)} minutes left to claim", ephemeral= True)
                return
        else:
            await interaction.response.send_message(f"You must create an account with '/openaccount'.", ephemeral= True)


@bot.tree.command(name='openaccount', description="Open an account")
async def openaccount(interaction:discord.Interaction):
    with open('data.json', 'r') as file:
        data = json.load(file)
        for ID in data['Accounts']:
            if str(interaction.user.id) == ID:
                await interaction.response.send_message(f"{interaction.user.mention} you already have an account")
                return
            else:
                pass
            break
    
    with open('cooldowns.json', 'r') as file1:
        profile = json.load(file1)
    
    with open('data.json', 'w') as file:
        
        data['Accounts'][str(interaction.user.id)] = {"Balance": 100}, {"last_claimed": 0}, {"status": "Peasant"}, {"chips": 0}
        json.dump(data, file)
        await interaction.response.send_message(f"{interaction.user.mention} account has been made. Use '/bal' to check your balance.")
    
    with open("cooldowns.json", "w") as file1:
        profile['Users'][str(interaction.user.id)] = {"last_claimed": 0}
        json.dump(profile, file1)
    
@bot.tree.command(name='bal', description="Check your account balance")
async def balance(interaction: discord.Interaction):
    with open('data.json', 'r') as file:
        data = json.load(file)
        ID = str(interaction.user.id)
        if ID in data["Accounts"]:
            val_1 = data['Accounts'][ID][0]['Balance']
            val_2 = data['Accounts'][ID][3]['chips']
            embed = discord.Embed(
                title=f"{interaction.user.name}'s Balance",
                color = discord.Color.dark_grey()
            )
            embed.add_field(name="Balances", value=f"🪙: {val_1} \n 🎱: {val_2}")
            embed.set_footer(text=interaction.user.name)
            await interaction.response.send_message(embed=embed)
            return

        await interaction.response.send_message(f"{interaction.user.mention}, you do not have an account. Use '/  openaccount' to make one.")

@bot.tree.command(name='give', description='Give someone some money out of your own pocket')
async def give(interaction: discord.Interaction, amount: int, member:discord.Member):
    person1 = str(interaction.user.id)
    person2 = str(member.id)

    if amount <= 0:
        await interaction.response.send_message("bro thought 💀") 

    with open('data.json', 'r') as file:
        data = json.load(file)

        if person1 in data['Accounts'] and person2 in data['Accounts']:
            if data['Accounts'][person1][0]['Balance'] >= amount:
                data['Accounts'][person1][0]['Balance'] -= amount
                data['Accounts'][person2][0]['Balance'] += amount
                await interaction.response.send_message(f"🪙{amount} has been sent to {member.mention}") 
            
            with open('data.json', 'w') as file:
                    json.dump(data, file)
        else:
            await interaction.response.send_message("Either one of you do not have an account", ephemeral=True)

@bot.tree.command(name="drop", description="Drop some money into the channel 💰")
async def drop(interaction: discord.Interaction, amount:int):
    person1 = str(interaction.user.id)

    if amount <= 0:
        await interaction.response.send_message("bro thought 💀")

    with open('data.json', 'r') as file:
        data = json.load(file)

        if person1 in data['Accounts']  :
            if data['Accounts'][person1][0]['Balance'] >= amount:
                data['Accounts'][person1][0]['Balance'] -= amount

                embed = discord.Embed(
                    title=f"@{interaction.user} has dropped **🪙{amount}**! **Claim it fast!**",
                    description="Claim it by pressing the button below!",
                    color=discord.Color.green()
                )
                
                embed.set_image(url="https://cdn.discordapp.com/attachments/1153197496198238249/1313909949352378501/image-removebg-preview1.png?ex=6751d97f&is=675087ff&hm=e554972bf90cf3629143b123c7dd441ea1811fc8219c0b7e4f07750e5b28ebd2&")
                global current_drop
                current_drop = amount

                await interaction.response.send_message(embed=embed, view=DView())

@bot.tree.command(name='work', description="Work for some money")
async def work(interaction: discord.Interaction):
    userId = interaction.user.id
    current_time = time.time()
    
    with open('data.json', 'r') as file1:
        profile = json.load(file1)
        
    with open('cooldowns.json', 'r') as file:
        data = json.load(file)

    if str(userId) in data['Users'] and str(userId) in profile['Accounts']:
        last_claim_time = data['Users'][str(userId)]['last_claimed']
        time_diff = int(current_time) - last_claim_time

        if last_claim_time == 0 or time_diff >= 7200:
            earnings = random.randint(0, 10000)
            data['Users'][str(userId)]['last_claimed'] = int(current_time)
            profile['Accounts'][str(userId)][0]['Balance'] += earnings
            
            embed = discord.Embed(
                    title=f"{interaction.user.name}'s Work",
                    color=discord.Color.green()
                )
            val = profile['Accounts'][str(userId)][0]['Balance']
            embed.add_field(name="Earnings", value=f"+${earnings} You have successfully earned money from work!")
            embed.add_field(name="Balance", value=f"🪙{val}", inline=False)
           
            await interaction.response.send_message(embed=embed)
            
            with open('data.json', 'w') as file1:
                json.dump(profile, file1)
                
            with open('cooldowns.json', 'w') as file:
                json.dump(data, file)
            
        else:
            await interaction.response.send_message("You have already claimed your reward. Please wait for the next claim.", ephemeral=True)
    
    else:
        await interaction.response.send_message("You must create an account with '/openaccount'.", ephemeral=True)

@bot.tree.command(name='beg', description='Beg and hope a kind stranger gives money')
async def beg(interaction: discord.Interaction):
    person1 = str(interaction.user.id)

    with open('data.json', 'r') as file:
        data = json.load(file)

    if person1 in data['Accounts']:
        amount = random.randint(1,100)
        name = ""
        new_amount = 0
        
        if amount <= 75:
            new_amount = random.randint(1,50)
            name="random person"
        elif amount <= 90 and amount > 75:
            new_amount = random.randint(50,100)
            name="nice stranger"
        elif amount <= 100 and amount > 90:
            new_amount = random.randint(100,500)
            name = "kind-hearted stranger"

        data['Accounts'][person1][0]['Balance'] += new_amount
        val = data['Accounts'][person1][0]['Balance']
        embed = discord.Embed(
            title=f"A {name} gave you some money",
            color=discord.Color.blurple()
        )
        embed.add_field(name="Earnings", value=f"They gave you 🪙{new_amount}.")
        embed.add_field(name="Balance", value=f"🪙{val}",inline= False)

        with open('data.json', 'w') as file:
            json.dump(data,file)

        await interaction.response.send_message(embed=embed)

#Gambling stuff
@bot.tree.command(name='deposit', description="Deposit some money to chips 🪙")
async def deposit(interaction: discord.Interaction, amount:int):
    person1 = str(interaction.user.id)

    if amount <= 0:
        await interaction.response.send_message("bro thought 💀")

    with open('data.json', 'r') as file:
        data = json.load(file)
        if person1 in data['Accounts']:
            if data['Accounts'][person1][0]['Balance'] >= amount:
                data['Accounts'][person1][0]['Balance'] -= amount
                data['Accounts'][person1][3]['chips'] += amount
                val = data['Accounts'][person1][0]['Balance']
                val_2 = data['Accounts'][person1][3]['chips']
                with open('data.json', 'w') as file:
                    json.dump(data,file)


                embed = discord.Embed(
                    title=f"@{interaction.user.name} currency exchange.",
                    color=discord.Color.green()
                )
                embed.add_field(name="Earnings", value=f"You have successfully transfered 🪙{amount} into 🎱.")
                embed.add_field(name="Balance", value=f"🪙{val} \n 🎱{val_2} ", inline=False)

                await interaction.response.send_message(embed=embed)   
            else:
                await interaction.response.send_message("You have an insufficient amount of gremlin tokens.")
        else:
            await interaction.response.send_message("Tip: Use /openaccount to open an account.")

@bot.tree.command(name='cashout', description="Cash out some chips for money 💸")
async def cashout(interaction: discord.Interaction, amount:int):
    person1 = str(interaction.user.id)

    if amount <= 0:
        await interaction.response.send_message("bro thought 💀")

    with open('data.json', 'r') as file:
        data = json.load(file)

        if person1 in data['Accounts']:
            if data['Accounts'][person1][3]['chips'] >= amount:
                data['Accounts'][person1][0]['Balance'] += amount
                data['Accounts'][person1][3]['chips'] -= amount
                val = data['Accounts'][person1][0]['Balance']
                val_2 = data['Accounts'][person1][3]['chips']
                
                with open('data.json', 'w') as file:
                    json.dump(data,file)
                
                embed = discord.Embed(
                    title=f"@{interaction.user.name} currency exchange.",
                    color=discord.Color.green()
                )
                embed.add_field(name="Earnings", value=f"You have successfully transfered 🎱{amount} into 🪙.")
                embed.add_field(name="Balance", value=f"🪙{val} \n 🎱{val_2} ", inline=False)

                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message("You have an insufficient amount of chips.")
        else:
            await interaction.response.send_message("Tip: Use /openaccount to open an account.")
        
@bot.tree.command(name='roulette', description="Pick colour Red/Black, choose number 0-36, enter money and win or lose.")
@app_commands.describe(
    amount="The amount you want to bet",
    number="The number you want to bet on (numbers 0-36)",
    color="The color you want to bet on (e.g., Red, Black)"
)
async def roulette(interaction: discord.Interaction, amount: int, number: int, color: str):
    person1 = str(interaction.user.id)
    bets = {}

    # Validate inputs
    if color.lower().strip() not in ["red", "black"]:
        await interaction.response.send_message("Enter either black or red.")
        return

    if number < 0 or number > 36:
        await interaction.response.send_message("Enter a valid integer between 0-36.")
        return

    with open('data.json', 'r') as file:
        data = json.load(file)

    if person1 not in data['Accounts']:
        await interaction.response.send_message("Account not found!")
        return

    if data['Accounts'][person1][3]['chips'] < int(amount):
        await interaction.response.send_message("You do not have enough money to place this bet.")
        return

    data['Accounts'][person1][3]['chips'] -= int(amount)
    bets[person1] = int(amount)

    embed_colour = discord.Color.red()
    TColour = random.choice(["red", "black"])
    Tnumber = random.randint(0, 36)

    colour_correct = (TColour == color)
    num_correct = (Tnumber == number)

    winnings = 0
    if colour_correct and num_correct:
        winnings = bets[person1] * 1.65
        embed_colour = discord.Color.green()
    elif colour_correct:
        winnings = bets[person1] * 1.30
        embed_colour = discord.Color.orange()

    data['Accounts'][person1][3]['chips'] += int(winnings)

    with open('data.json', 'w') as file:
        json.dump(data, file)

    embed = discord.Embed(
        title=f"{interaction.user.name}'s roulette game",
        colour=embed_colour,
    )
    embed.add_field(name="Winnings", value=f"Correct colour was {TColour}, correct number was {Tnumber}. You chose {number} and {color}. You won 🎱{winnings}.")
    balc = data['Accounts'][person1][3]['chips']
    embed.add_field(name="Balance", value=f"🎱: {balc}", inline= False)
    embed.set_footer(text=f"Bet:{amount}")

    bets[person1] = None    

    await interaction.response.send_message(embed=embed)


##Admin stuff LOLLLLLLLLLL
@bot.command(name="add")
async def add(ctx, amount:int, member:discord.Member):


    if ctx.author.id != 452363360458113034:
        return
    person1 = str(ctx.author.id)
    person2 = str(member.id)

    if amount <= 0:
        await ctx.send("bro thought 💀")

    with open('data.json', 'r') as file:
        data = json.load(file)

        if person1 in data['Accounts'] and person2 in data['Accounts']:
            data['Accounts'][person2][0]['Balance'] += amount
            await ctx.send(f"🪙{amount} has been given to {member.mention}") 
            
            with open('data.json', 'w') as file:
                    json.dump(data, file)

@bot.command(name="addC")
async def add(ctx, amount:int, member:discord.Member):


    if ctx.author.id != 452363360458113034:
        return
     
    person1 = str(ctx.author.id)
    person2 = str(member.id)

    if amount <= 0:
        await ctx.send("bro thought 💀")

    with open('data.json', 'r') as file:
        data = json.load(file)

        if person1 in data['Accounts'] and person2 in data['Accounts']:
            data['Accounts'][person2][3]['chips'] += amount
            await ctx.send(f"🎱{amount} has been given to {member.mention}") 
            
            with open('data.json', 'w') as file:
                    json.dump(data, file)

@bot.command(name="set")
async def add(ctx, amount:int, member:discord.Member):


    if ctx.author.id != 452363360458113034:
        return
     
    person1 = str(ctx.author.id)
    person2 = str(member.id)

    if amount <= 0:
        await ctx.send("bro thought 💀")

    with open('data.json', 'r') as file:
        data = json.load(file)

        if person1 in data['Accounts'] and person2 in data['Accounts']:
            data['Accounts'][person2][0]['Balance'] = amount
            await ctx.send(f"🪙{amount} is now {member.mention} balance") 
            
            with open('data.json', 'w') as file:
                    json.dump(data, file)

@bot.command(name="setC")
async def add(ctx, amount:int, member:discord.Member):


    if ctx.author.id != 452363360458113034:
        return
     
    person1 = str(ctx.author.id)
    person2 = str(member.id)

    if amount <= 0:
        await ctx.send("bro thought 💀")

    with open('data.json', 'r') as file:
        data = json.load(file)

        if person1 in data['Accounts'] and person2 in data['Accounts']:
            data['Accounts'][person2][3]['chips'] = amount
            await ctx.send(f"🎱{amount} is now {member.mention}'s chip balance.") 
            
            with open('data.json', 'w') as file:
                    json.dump(data, file)



bot.run(token=token) 
