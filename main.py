"""
Platformer Game
"""

import arcade
import math
import random

# Constants
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 490
SCREEN_TITLE = "Platformer"

# Constants used to scale our sprites from their original size
CHARACTER_SCALING = 2
TILE_SCALING = 2
COIN_SCALING = 2

# End of the map is 5000 according to player_sprite.center_x
END_OF_MAP = 5040

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 8
GRAVITY = 1
PLAYER_JUMP_SPEED = 18

# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
LEFT_VIEWPORT_MARGIN = 200
RIGHT_VIEWPORT_MARGIN = 200
BOTTOM_VIEWPORT_MARGIN = 150
TOP_VIEWPORT_MARGIN = 100

# Player starting position -def is 350 for x
PLAYER_START_X = 350
PLAYER_START_Y = 300

# Layer Names from our TileMap
LAYER_NAME_PLATFORMS = "Platforms"
LAYER_NAME_MOVING_PLATFORMS = "Moving Platforms"
LAYER_NAME_COINS = "Coins"
LAYER_NAME_DEATH = "Death"
LAYER_NAME_ENEMIES = "Enemies"
LAYER_NAME_STATUES = "Statues"

# Player Layer
LAYER_NAME_PLAYER = "Player"

# Constants used to track if the player is facing left or right
RIGHT_FACING = 0
LEFT_FACING = 1


class GameOverView(arcade.View):

    def __init__(self):
        super().__init__()
        self.texture = arcade.load_texture("data/gameover.jpg")

    def on_show_view(self):
        """ This is run once when we switch to this view """
        self.window.background_color = arcade.csscolor.DARK_SLATE_BLUE

        # Reset the viewport, necessary if we have a scrolling game ,and we need
        # to reset the viewport back to the start, so we can see what we draw.
        arcade.set_viewport(0, self.window.width, 0, self.window.height)

    def on_draw(self):
        """ Draw this view """
        self.clear()
        self.texture.draw_scaled(450, 245)

        game_over = arcade.Text(
            "GAME OVER",
            250,
            100,
            arcade.color.ASH_GREY,
            45,
            font_name="Kenney Rocket",
        )

        game_over.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE or key == arcade.key.Q:
            arcade.exit()
        elif key == arcade.key.SPACE:
            game_view = GameView()
            game_view.setup()
            self.window.show_view(game_view)


class InstructionView(arcade.View):

    def __init__(self):
        super().__init__()
        self.texture = arcade.load_texture("data/bg.jpg")
        self.songs = ["data/music/track1.mp3",
                      "data/music/track2.mp3",
                      "data/music/track3.mp3",
                      "data/music/track4.mp3",
                      "data/music/track5.mp3",
                      "data/music/track6.mp3",
                      "data/music/track7.mp3",
                      "data/music/track8.mp3",
                      "data/music/track9.mp3",
                      "data/music/track10.mp3",
                      "data/music/track11.mp3",
                      "data/music/track12.mp3"]
        self.cur_song_index = random.randint(0, 11)
        self.my_music = arcade.load_sound(self.songs[self.cur_song_index])

    def on_show_view(self):
        """ This is run once when we switch to this view """
        self.window.background_color = arcade.csscolor.DARK_SLATE_BLUE

        # Load music

        arcade.play_sound(self.my_music, looping=True)

        # Reset the viewport, necessary if we have a scrolling game, and we need
        # to reset the viewport back to the start, so we can see what we draw.
        arcade.set_viewport(0, self.window.width, 0, self.window.height)

    def on_draw(self):
        """ Draw this view """
        self.clear()
        self.texture.draw_scaled(450, 245)

        game_name = arcade.Text(
            "SILENT VALLEY",
            550,
            430,
            arcade.color.ASH_GREY,
            25,
            font_name="Kenney Future",
        )

        start_game = arcade.Text(
            "PRESS SPACE TO START PLAYING",
            550,
            380,
            arcade.color.ASH_GREY,
            15,
            font_name="Kenney Mini",
        )

        exit_game = arcade.Text(
            "PRESS ESC OR Q TO EXIT",
            610,
            330,
            arcade.color.ASH_GREY,
            15,
            font_name="Kenney Mini",
        )

        game_name.draw()
        start_game.draw()
        exit_game.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE or key == arcade.key.Q:
            arcade.exit()
        elif key == arcade.key.SPACE:
            game_view = GameView()
            game_view.setup()
            self.window.show_view(game_view)


class Entity(arcade.Sprite):

    def __init__(self, name_folder, name_file):
        super().__init__()

        # Default to facing right

        self.facing_direction = RIGHT_FACING

        # Used for image sequences

        self.cur_texture = 0
        self.scale = 3
        self.character_face_direction = RIGHT_FACING

        main_path = f"data/{name_folder}/{name_file}"

        self.idle_texture_pair = arcade.load_texture_pair(f"{main_path}_flying1.png")
        # self.death_texture_pair = arcade.load_texture_pair(f"{main_path}_death1.png")

        # Load textures for walking
        self.walk_textures = []

        for i in range(1, 5):
            texture = arcade.load_texture_pair(f"{main_path}_flying{i}.png")
            self.walk_textures.append(texture)

        # Set the initial texture
        self.texture = self.idle_texture_pair[0]

        # Hit box will be set based on the first image used. If you want to specify

        # a different hit box, you can do it like the code below. Doing this when

        # changing the texture for example would make the hitbox update whenever the

        # texture is changed. This can be expensive so if the textures are very similar

        # it may not be worth doing.

        #

        # self.hit_box = arcade.hitbox.RotatableHitBox(

        #     self.texture.hit_box_points,

        #     position=self.position,

        #     scale=self.scale_xy,

        #     angle=self.angle,

        # )


class Enemy(Entity):

    def __init__(self, name_folder, name_file):

        # Setup parent class

        super().__init__(name_folder, name_file)

        self.should_update_walk = 0

    def update_animation(self, delta_time: float = 1 / 60):

        # Figure out if we need to flip face left or right

        if self.change_x < 0 and self.facing_direction == RIGHT_FACING:

            self.facing_direction = LEFT_FACING

        elif self.change_x > 0 and self.facing_direction == LEFT_FACING:

            self.facing_direction = RIGHT_FACING

        # Idle animation

        if self.change_x == 0:
            self.texture = self.idle_texture_pair[self.facing_direction]

            return

        # Walking animation

        if self.should_update_walk == 3:

            self.cur_texture += 1

            if self.cur_texture > 3:
                self.cur_texture = 0

            self.texture = self.walk_textures[self.cur_texture][self.facing_direction]

            self.should_update_walk = 0

            return

        self.should_update_walk += 1


class BatEnemy(Enemy):

    def __init__(self):
        # Set up parent class

        super().__init__("bat", "bat")


class PlayerCharacter(arcade.Sprite):
    """Player Sprite"""

    def __init__(self):

        # Set up parent class

        super().__init__()

        # Default to face-right

        self.character_face_direction = RIGHT_FACING

        # Used for flipping between image sequences

        self.cur_texture = 0

        self.scale = CHARACTER_SCALING

        # Track our state

        self.jumping = False

        self.climbing = False

        self.is_on_ladder = False

        # --- Load Textures ---

        # Images from Kenney.nl's Asset Pack 3

        main_path = "data"

        # Load textures for idle standing

        self.idle_texture_pair = arcade.load_texture_pair(f"{main_path}/princess/idle/idle1.png")

        self.jump_texture_pair = arcade.load_texture_pair(f"{main_path}/princess/jump/jump1.png")

        self.fall_texture_pair = arcade.load_texture_pair(f"{main_path}/princess/fall/fall1.png")

        # Load textures for walking

        self.walk_textures = []

        for i in range(1, 8):
            texture = arcade.load_texture_pair(f"{main_path}/princess/walk/walk{i}.png")

            self.walk_textures.append(texture)

        # Set the initial texture

        self.texture = self.idle_texture_pair[0]

        # Hit box will be set based on the first image used. If you want to specify

        # a different hit box, you can do it like the code below. Doing this when

        # changing the texture for example would make the hitbox update whenever the

        # texture is changed. This can be expensive so if the textures are very similar

        # it may not be worth doing.

        #

        # self.hit_box = arcade.hitbox.RotatableHitBox(

        #     self.texture.hit_box_points,

        #     position=self.position,

        #     scale=self.scale_xy,

        #     angle=self.angle,

        # )

    def update_animation(self, delta_time: float = 1 / 60):

        # Figure out if we need to flip face left or right

        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:

            self.character_face_direction = LEFT_FACING

        elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:

            self.character_face_direction = RIGHT_FACING

        # Jumping animation

        if self.change_y > 0 and not self.is_on_ladder:

            self.texture = self.jump_texture_pair[self.character_face_direction]

            return

        elif self.change_y < 0 and not self.is_on_ladder:

            self.texture = self.fall_texture_pair[self.character_face_direction]

            return

        # Idle animation

        if self.change_x == 0:
            self.texture = self.idle_texture_pair[self.character_face_direction]

            return

        # Walking animation

        self.cur_texture += 1

        if self.cur_texture > 6:
            self.cur_texture = 0

        self.texture = self.walk_textures[self.cur_texture][

            self.character_face_direction

        ]


class GameView(arcade.View):
    """
    Main application class.
    """

    def __init__(self):

        # Call the parent class and set up the window
        super().__init__()

        # Disable mouse
        self.window.set_mouse_visible(False)

        # Track the current state of what key is pressed

        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.jump_needs_reset = False

        # Our TileMap Object
        self.tile_map = None

        # Our Scene Object
        self.scene = None

        # Separate variable that holds the player sprite
        self.player_sprite = None

        # Our physics engine
        self.physics_engine = None

        # A Camera that can be used for scrolling the screen
        self.camera = None

        # A Camera that can be used to draw GUI elements
        self.gui_camera = None

        # Keep track of the score
        self.score = 0

        # Reset score
        self.reset_score = True

        # Where is the right edge of the map?
        self.end_of_map = 0

        # Level
        self.level = 1

        # Load sounds
        self.collect_coin_sound = arcade.load_sound(":resources:sounds/coin1.wav")
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")
        self.game_over = arcade.load_sound(":resources:sounds/gameover1.wav")

        self.background_color = arcade.csscolor.CORNFLOWER_BLUE

    def setup(self):
        """Set up the game here. Call this function to restart the game."""

        # Set up the Cameras
        viewport = (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.camera = arcade.SimpleCamera(viewport=viewport)
        self.gui_camera = arcade.SimpleCamera(viewport=viewport)

        # Name of map file to load
        # map_name = f"/data/map{self.level}.json"
        map_name = f"data/map1.json"

        # Layer specific options are defined based on Layer names in a dictionary
        # Doing this will make the SpriteList for the platforms layer
        # use spatial hashing for detection.
        layer_options = {
            LAYER_NAME_PLATFORMS: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_MOVING_PLATFORMS: {
                "use_spatial_hash": False,
            },
            LAYER_NAME_COINS: {
                "use_spatial_hash": True,
                "scaling": COIN_SCALING
            }
        }

        # Read in the tiled map
        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, layer_options)

        # Initialize Scene with our TileMap, this will automatically add all layers
        # from the map as SpriteLists in the scene in the proper order.
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # Keep track of the score
        if self.reset_score:
            self.score = 0

        self.reset_score = True

        # Set up the player, specifically placing it at these coordinates.
        self.player_sprite = PlayerCharacter()
        self.player_sprite.center_x = PLAYER_START_X
        self.player_sprite.center_y = PLAYER_START_Y
        self.scene.add_sprite(LAYER_NAME_PLAYER, self.player_sprite)

        # Calculate the ending point for the game
        self.end_of_map = END_OF_MAP

        # -- Enemies

        enemies_layer = self.tile_map.object_lists[LAYER_NAME_ENEMIES]

        for my_object in enemies_layer:

            cartesian = self.tile_map.get_cartesian(

                my_object.shape[0], my_object.shape[1]

            )

            enemy_type = my_object.properties["type"]

            if enemy_type == "bat":
                enemy = BatEnemy()

            enemy.center_x = math.floor(

                cartesian[0] * TILE_SCALING * self.tile_map.tile_width

            )

            enemy.center_y = math.floor(

                (cartesian[1] + 1) * (self.tile_map.tile_height * TILE_SCALING)

            )

            if "boundary_left" in my_object.properties:
                enemy.boundary_left = my_object.properties["boundary_left"]

            if "boundary_right" in my_object.properties:
                enemy.boundary_right = my_object.properties["boundary_right"]

            if "change_x" in my_object.properties:
                enemy.change_x = my_object.properties["change_x"]

            self.scene.add_sprite(LAYER_NAME_ENEMIES, enemy)

        # --- Other stuff
        # Set the background color
        if self.tile_map.background_color:
            self.background_color = self.tile_map.background_color

        # Create the 'physics engine'
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite, gravity_constant=GRAVITY,
            walls=self.scene["Platforms"],
            platforms=self.scene[LAYER_NAME_MOVING_PLATFORMS]
        )

    def on_draw(self):
        """Render the screen."""

        # Clear the screen to the background color
        self.clear()

        # Activate the game camera
        self.camera.use()

        # Draw our Scene
        self.scene.draw()

        # Activate the GUI camera before drawing GUI elements
        self.gui_camera.use()

        # Draw our score on the screen, scrolling it with the viewport
        score_x = 10
        score_y = 10
        default_font_size = 13
        score_text = arcade.Text(
            f"Score: {self.score}",
            score_x,
            score_y,
            arcade.color.BLACK,
            default_font_size,
            font_name="Kenney Future",
        )

        score_text.draw()

    def process_keychange(self):

        """

        Called when we change a key up/down, or we move on/off a ladder.

        """

        # Process up/down

        if self.up_pressed and not self.down_pressed:

            if self.physics_engine.can_jump(y_distance=10) and not self.jump_needs_reset:
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                self.jump_needs_reset = True
                arcade.play_sound(self.jump_sound)

        # Process left/right

        if self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

        elif self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED

        else:

            self.player_sprite.change_x = 0

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""

        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = True

        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = True

        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True

        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True
        elif key == arcade.key.ESCAPE or key == arcade.key.Q:
            arcade.exit()

        self.process_keychange()

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key."""

        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = False
            self.jump_needs_reset = False

        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = False

        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False

        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False

        self.process_keychange()

    def center_camera_to_player(self):
        screen_center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (self.camera.viewport_height / 2)
        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0
        player_centered = screen_center_x, screen_center_y
        self.camera.move_to(player_centered)

    def on_update(self, delta_time):
        """Movement and game logic"""

        # Update animations
        self.scene.update_animation(delta_time,
                                    [LAYER_NAME_COINS, LAYER_NAME_STATUES, LAYER_NAME_PLAYER, LAYER_NAME_DEATH,
                                     LAYER_NAME_ENEMIES])

        if self.physics_engine.can_jump():
            self.player_sprite.can_jump = False

        else:
            self.player_sprite.can_jump = True

        self.scene.update([LAYER_NAME_MOVING_PLATFORMS, LAYER_NAME_ENEMIES])

        # See if the enemy hit a boundary and needs to reverse direction.

        for enemy in self.scene[LAYER_NAME_ENEMIES]:

            if (
                    enemy.boundary_right
                    and enemy.right > enemy.boundary_right
                    and enemy.change_x > 0
            ):
                enemy.change_x *= -1

            if (
                    enemy.boundary_left
                    and enemy.left < enemy.boundary_left
                    and enemy.change_x < 0
            ):
                enemy.change_x *= -1

        # Move the player with the physics engine
        self.physics_engine.update()

        # See if we hit any coins
        coin_hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene[LAYER_NAME_COINS]
        )

        # Loop through each coin we hit (if any) and remove it
        for coin in coin_hit_list:
            # Remove the coin
            coin.remove_from_sprite_lists()
            # Play a sound
            arcade.play_sound(self.collect_coin_sound)
            # Add one to the score
            self.score += 1

        # Did the player fall off the map?
        if self.player_sprite.center_y < -100:
            self.player_sprite.center_x = PLAYER_START_X
            self.player_sprite.center_y = PLAYER_START_Y
            arcade.play_sound(self.game_over)
            game_view = GameOverView()
            self.window.show_view(game_view)

        # Did the player touch something they should not?
        if arcade.check_for_collision_with_lists(
                self.player_sprite,
                [
                    self.scene[LAYER_NAME_ENEMIES],
                    self.scene[LAYER_NAME_DEATH]
                ]):
            self.player_sprite.change_x = 0
            self.player_sprite.change_y = 0
            self.player_sprite.center_x = PLAYER_START_X
            self.player_sprite.center_y = PLAYER_START_Y
            arcade.play_sound(self.game_over)
            game_view = GameOverView()
            self.window.show_view(game_view)

        # See if the user got to the end of the level (5000 is the actual end for player_sprite.center_x)
        if self.player_sprite.center_x >= self.end_of_map:
            # Advance to the next level
            self.level += 1

            # Make sure to keep the score from this level when setting up the next level
            self.reset_score = False

        # Position the camera
        self.center_camera_to_player()


def main():
    """Main function"""
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    start_view = InstructionView()
    window.show_view(start_view)
    arcade.run()


if __name__ == "__main__":
    main()
