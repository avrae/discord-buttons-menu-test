"""Counter example given at https://github.com/Rapptz/discord.py/blob/master/examples/views/ephemeral.py"""
import discord


# Define a simple View that gives us a counter button
class Counter(discord.ui.View):

    # Define the actual button
    # When pressed, this increments the number displayed until it hits 5.
    # When it hits 5, the counter button is disabled and it turns green.
    # note: The name of the function does not matter to the library
    @discord.ui.button(label='0', style=discord.ButtonStyle.red)
    async def count(self, button: discord.ui.Button, interaction: discord.Interaction):
        number = int(button.label) if button.label else 0
        if number + 1 >= 5:
            button.style = discord.ButtonStyle.green
            button.disabled = True
        button.label = str(number + 1)

        # Make sure to update the message with our updated selves
        await interaction.response.edit_message(view=self)


# Define a View that will give us our own personal counter button
class EphemeralCounter(discord.ui.View):
    # When this button is pressed, it will respond with a Counter view_type that will
    # give the button presser their own personal button they can press 5 times.
    @discord.ui.button(label='Click', style=discord.ButtonStyle.blurple)
    async def receive(self, button: discord.ui.Button, interaction: discord.Interaction):
        # ephemeral=True makes the message hidden from everyone except the button presser
        await interaction.response.send_message('Enjoy!', view=Counter(), ephemeral=True)
