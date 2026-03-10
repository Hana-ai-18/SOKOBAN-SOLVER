import pygame
import constants as SOKOBAN

class PlayerInterface:
    def __init__(self, player, level):
        self.player = player
        self.level  = level
        self.mouse_pos = (-1, -1)

        self.font_menu  = pygame.font.Font(
            'sokoban\\assets\\fonts\\FreeSansBold.ttf', 18)
        self.font_small = pygame.font.Font(
            'sokoban\\assets\\fonts\\FreeSansBold.ttf', 13)

       
        self.txtLevel       = "Level 1"
        self.colorTxtLevel  = SOKOBAN.BLACK

        self.txtCancel       = "Undo (L)"
        self.colorTxtCancel  = SOKOBAN.GREY

        self.txtReset        = "Restart (R)"
        self.colorTxtReset   = SOKOBAN.BLACK


        self.txtAutoDFS      = "Auto DFS"
        self.colorTxtAutoDFS = SOKOBAN.BLACK

        self.txtAutoBFS      = "Auto BFS"
        self.colorTxtAutoBFS = SOKOBAN.BLACK

        self.txtAutoUCS      = "Auto UCS"
        self.colorTxtAutoUCS = SOKOBAN.BLACK

       
        self.txtPrev         = "< Level"
        self.colorTxtPrev    = SOKOBAN.BLACK

        self.txtNext         = "Level >"
        self.colorTxtNext    = SOKOBAN.BLACK

  
    def click(self, pos_click, level, game):
        x, y = pos_click

        # Undo
        if self._hit(x, y, self.posTxtCancel, self.txtCancelSurface):
            level.cancel_last_move(self.player, self)
            if game.steps > 0:
                game.steps -= 1
            self.colorTxtCancel = SOKOBAN.GREY

        #  Restart 
        if self._hit(x, y, self.posTxtReset, self.txtResetSurface):
            game.load_level()

        #  Auto DFS 
        if self._hit(x, y, self.posTxtAutoDFS, self.txtAutoDFSSurface):
            game.load_level()        
            game.auto_move('dfs')

        #  Auto BFS 
        if self._hit(x, y, self.posTxtAutoBFS, self.txtAutoBFSSurface):
            game.load_level()
            game.auto_move('bfs')

        #  Auto UCS 
        if self._hit(x, y, self.posTxtAutoUCS, self.txtAutoUCSSurface):
            game.load_level()
            game.auto_move('ucs')

        #  Level trước 
        if self._hit(x, y, self.posTxtPrev, self.txtPrevSurface):
            game.index_level = max(1, game.index_level - 1)
            game.load_level()

        #  Level sau 
        if self._hit(x, y, self.posTxtNext, self.txtNextSurface):
            game.index_level = min(18, game.index_level + 1)
            game.load_level()

   
    def _hit(self, x, y, pos, surface):
        return (pos[0] < x < pos[0] + surface.get_width() and
                pos[1] < y < pos[1] + surface.get_height())

  
    def render(self, window, level):
        #  Level label 
        self.txtLevel = f"Level {level}"
        self.txtLevelSurface = self.font_menu.render(
            self.txtLevel, True, self.colorTxtLevel, SOKOBAN.WHITE)
        window.blit(self.txtLevelSurface, (10, 10))

        #  Undo  
        self.txtCancelSurface = self.font_menu.render(
            self.txtCancel, True, self.colorTxtCancel, SOKOBAN.WHITE)
        self.posTxtCancel = (
            SOKOBAN.WINDOW_WIDTH - self.txtCancelSurface.get_width() - 10, 10)
        window.blit(self.txtCancelSurface, self.posTxtCancel)

        #  Restart
        self.txtResetSurface = self.font_menu.render(
            self.txtReset, True, self.colorTxtReset, SOKOBAN.WHITE)
        self.posTxtReset = (
            SOKOBAN.WINDOW_WIDTH / 2 - self.txtResetSurface.get_width() / 2, 10)
        window.blit(self.txtResetSurface, self.posTxtReset)

        
        btn_y = 36
        total_w = SOKOBAN.WINDOW_WIDTH
        spacing = total_w // 4

        self.txtAutoDFSSurface = self.font_menu.render(
            self.txtAutoDFS, True, self.colorTxtAutoDFS, SOKOBAN.WHITE)
        self.posTxtAutoDFS = (spacing - self.txtAutoDFSSurface.get_width() // 2, btn_y)
        window.blit(self.txtAutoDFSSurface, self.posTxtAutoDFS)

        self.txtAutoBFSSurface = self.font_menu.render(
            self.txtAutoBFS, True, self.colorTxtAutoBFS, SOKOBAN.WHITE)
        self.posTxtAutoBFS = (spacing * 2 - self.txtAutoBFSSurface.get_width() // 2, btn_y)
        window.blit(self.txtAutoBFSSurface, self.posTxtAutoBFS)

        self.txtAutoUCSSurface = self.font_menu.render(
            self.txtAutoUCS, True, self.colorTxtAutoUCS, SOKOBAN.WHITE)
        self.posTxtAutoUCS = (spacing * 3 - self.txtAutoUCSSurface.get_width() // 2, btn_y)
        window.blit(self.txtAutoUCSSurface, self.posTxtAutoUCS)

      
        nav_y = SOKOBAN.WINDOW_HEIGHT - 28

        self.txtPrevSurface = self.font_small.render(
            self.txtPrev, True, self.colorTxtPrev, SOKOBAN.WHITE)
        self.posTxtPrev = (
            SOKOBAN.WINDOW_WIDTH // 2 - self.txtPrevSurface.get_width() - 20, nav_y)
        window.blit(self.txtPrevSurface, self.posTxtPrev)

        self.txtNextSurface = self.font_small.render(
            self.txtNext, True, self.colorTxtNext, SOKOBAN.WHITE)
        self.posTxtNext = (
            SOKOBAN.WINDOW_WIDTH // 2 + 20, nav_y)
        window.blit(self.txtNextSurface, self.posTxtNext)