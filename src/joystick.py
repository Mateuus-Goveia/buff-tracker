import os
import threading
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
import pygame

DPAD_REVERSE = {
    (0, 1): "up",
    (0, -1): "down",
    (-1, 0): "left",
    (1, 0): "right"
}

def start_joystick_listener(app_callback):
    def listen():
        pygame.init()
        pygame.joystick.init()
        last_hat_state = (0, 0)
        last_button_states = {}

        while getattr(app_callback, "running_joystick", True):
            if pygame.joystick.get_count() > 0:
                try:
                    js = pygame.joystick.Joystick(0)
                    js.init()
                    pygame.event.pump()

                    l2_pressed = False
                    r2_pressed = False
                    if js.get_numaxes() >= 3:
                        if js.get_axis(2) > 0.5:
                            l2_pressed = True
                    if js.get_numaxes() >= 6:
                        if js.get_axis(5) > 0.5:
                            r2_pressed = True

                    active_mod = "none"
                    if l2_pressed:
                        active_mod = "l2"
                    elif r2_pressed:
                        active_mod = "r2"

                    if js.get_numhats() > 0:
                        current_hat = js.get_hat(0)
                        if current_hat != (0, 0) and current_hat != last_hat_state:
                            dpad_name = DPAD_REVERSE.get(current_hat)
                            if dpad_name:
                                app_callback.trigger_buff_by_input(dpad_name, active_mod)
                        last_hat_state = current_hat

                    for btn_idx in range(min(4, js.get_numbuttons())):
                        btn_state = js.get_button(btn_idx)
                        was_pressed = last_button_states.get(btn_idx, 0)
                        if btn_state == 1 and was_pressed == 0:
                            btn_name_map = {0: "a", 1: "b", 2: "x", 3: "y"}
                            b_name = btn_name_map.get(btn_idx)
                            if b_name:
                                app_callback.trigger_buff_by_input(b_name, active_mod)
                        last_button_states[btn_idx] = btn_state

                except Exception:
                    pass
            pygame.time.wait(50)

    thread = threading.Thread(target=listen, daemon=True)
    thread.start()
    return thread