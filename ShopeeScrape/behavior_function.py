from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import random
import time

def simulate_human_behavior(driver, num_actions=10):
    print("Simulating human-like behavior...")
    actions = ActionChains(driver)
    for _ in range(num_actions):
        scroll_y = int(random.uniform(100, 800))  
        try:
            driver.execute_script(f"window.scrollBy(0, {scroll_y});")
        except Exception as e:
            print(f"Scroll error: {e}") 
        time.sleep(random.uniform(0.5, 2))

    try:
        elements = driver.find_elements(By.CSS_SELECTOR, "div")
        for _ in range(num_actions):
            if elements:
                element = random.choice(elements)
                try:
                    actions.move_to_element(element).pause(random.uniform(0.5, 2)).perform()
                except Exception as e:
                    print(f"Mouse move error: {e}")
    except Exception as e:
        print(f"Element find error: {e}")
    
    print("Human-like actions completed.")