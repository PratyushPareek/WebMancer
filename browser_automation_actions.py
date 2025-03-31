
class BrowserAutomationActions:
    
    def __init__(self, headless: bool = False, browser_type: str = "chromium", log_level: str = "INFO"):
        """
        Initialize the browser automation agent.
        
        Args:
            headless: Whether to run the browser in headless mode
            browser_type: Type of browser to use (chromium, firefox, or webkit)
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.headless = headless
        self.browser_type = browser_type
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.command_history = []
        self.last_error = None
        
        # Initialize logger
        import logging
        self.logger = logging.getLogger(__name__)
        logging_level = getattr(logging, log_level.upper(), logging.INFO)
        self.logger.setLevel(logging_level)
        
        # Create console handler if no handlers exist
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging_level)
            formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
    
    async def start(self) -> bool:
        """Start the browser and create a new page."""
        print("Starting browser...")
        try:
            from playwright.async_api import async_playwright
            
            self.playwright = await async_playwright().start()
            browser_options = {
                "chromium": self.playwright.chromium,
                "firefox": self.playwright.firefox,
                "webkit": self.playwright.webkit
            }
            
            if self.browser_type not in browser_options:
                self.logger.error(f"Unsupported browser type: {self.browser_type}")
                return False
                
            self.browser = await browser_options[self.browser_type].launch(headless=self.headless)
            self.context = await self.browser.new_context()
            self.page = await self.context.new_page()
            self.logger.info(f"Started {self.browser_type} browser {'in headless mode' if self.headless else 'in visible mode'}")
            return True
        except Exception as e:
            self.last_error = str(e)
            # self.logger.error(f"Failed to start browser: {e}")
            return False
        
    async def navigate(self, url: str, timeout: int = 30000, wait_until: str = "load") -> bool:
        """
        Navigate to a specified URL.
        
        Args:
            url: The URL to navigate to
            timeout: Maximum navigation time in milliseconds
            wait_until: Navigation wait condition ('load', 'domcontentloaded', 'networkidle', 'commit')
            
        Returns:
            True if navigation successful, False otherwise
        """
        try:
            # Ensure URL has http or https prefix
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                self.logger.info(f"Added https prefix to URL: {url}")
                
            self.logger.info(f"Navigating to {url}")
            # Wait for the page navigation to complete with specified wait condition
            response = await self.page.goto(
                url, 
                timeout=timeout,
                wait_until=wait_until
            )
            
            # Check if navigation was successful
            if response:
                status = response.status
                if 200 <= status < 400:
                    self.logger.info(f"Successfully navigated to {url} (status {status})")
                    self.command_history.append(f"navigate('{url}')")
                    return True
                else:
                    self.last_error = f"Navigation returned status code {status}"
                    self.logger.warning(f"Navigation to {url} returned status code {status}")
                    return False
            else:
                self.last_error = "Navigation did not return a response"
                self.logger.warning(f"Navigation to {url} did not return a response")
                return False
                
        except Exception as e:
            self.last_error = str(e)
            self.logger.error(f"Failed to navigate to {url}: {e}")
            return False
    
    async def stop(self) -> bool:
        """Close the browser and stop the playwright instance."""
        try:
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            self.logger.info("Browser session stopped")
            return True
        except Exception as e:
            self.last_error = str(e)
            self.logger.error(f"Failed to stop browser: {e}")
            return False

    async def _smart_click(self, target: str) -> bool:
        """
        Intelligently find and click a target element using multiple strategies.
        
        Args:
            target: Description of the element to click
            
        Returns:
            True if click was successful, False otherwise
        """
        # Sanitize the target string for XPath safety
        print("Smart click", target)
        safe_target = target.replace("'", "\\'")
        
        # Try to find the element using different strategies
        element = None
        
        try:
            
            # Strategy 3: Look for buttons and links using role
            for role in ["button", "link"]:
                try:
                    elements = self.page.get_by_role(role, name=target, exact=True)
                    count = await elements.count()
                    if count > 0:
                        await elements.first.click()
                        self.logger.info(f"Clicked on {role} with name: {target}")
                        return True
                except Exception as e:
                    self.logger.info(f"Strategy 3 ({role} role) failed: {e}")

            # Strategy 3: Look for buttons and links using role (partial match)
            for role in ["button", "link"]:
                try:
                    elements = self.page.get_by_role(role, name=target, exact=False)
                    count = await elements.count()
                    if count > 0:
                        await elements.first.click()
                        self.logger.info(f"Clicked on {role} with name: {target}")
                        return True
                except Exception as e:
                    self.logger.info(f"Strategy 3 ({role} role) failed: {e}")
            
            # Strategy 4: Look for exact text match with XPath (fallback)
            element = await self.page.query_selector(f"//*[text()='{safe_target}']")
            if element:
                await element.click()
                self.logger.info(f"Clicked on element with exact text (XPath): {target}")
                return True
            
            # Strategy 5: Look for contains text with XPath
            element = await self.page.query_selector(f"//*[contains(text(), '{safe_target}')]")
            if element:
                await element.click()
                self.logger.info(f"Clicked on element containing text (XPath): {target}")
                return True
            
            # Strategy 6: Look for button with text
            element = await self.page.query_selector(f"button:has-text('{safe_target}')")
            if element:
                await element.click()
                self.logger.info(f"Clicked on button with text: {target}")
                return True
            
            # Strategy 7: Look for link with text
            element = await self.page.query_selector(f"a:has-text('{safe_target}')")
            if element:
                await element.click()
                self.logger.info(f"Clicked on link with text: {target}")
                return True
            
            # Strategy 8: Look for input elements with matching placeholder or value
            element = await self.page.query_selector(f"input[placeholder='{safe_target}'], input[value='{safe_target}']")
            if element:
                await element.click()
                self.logger.info(f"Clicked on input with placeholder/value: {target}")
                return True
            
            # Strategy 9: Look for elements with title, aria-label, or name attributes
            element = await self.page.query_selector(
                f"[title='{safe_target}'], [aria-label='{safe_target}'], [name='{safe_target}'], [id='{safe_target}']"
            )
            if element:
                await element.click()
                self.logger.info(f"Clicked on element with matching attribute: {target}")
                return True
            
            # Strategy 10: Case-insensitive attribute search
            element = await self.page.query_selector(
                f"[title='{safe_target}' i], [aria-label='{safe_target}' i], [placeholder='{safe_target}' i]"
            )
            if element:
                await element.click()
                self.logger.info(f"Clicked on element with case-insensitive attribute: {target}")
                return True
            
            # If we get here, no element was found
            self.logger.error(f"Could not find element to click: {target}")
            return False
        
        except Exception as e:
            self.logger.error(f"Error while trying to click '{target}': {str(e)}")
            return False
    
    async def _smart_fill(self, field: str, text: str) -> bool:
        """
        Intelligently find and fill a form field.
        
        Args:
            field: Description of the field to fill
            text: Text to enter into the field
                
        Returns:
            True if fill was successful, False otherwise
        """
        # Sanitize the field string for selector safety
        safe_field = field.replace("'", "\\'")
        print("Smart fill in field", field)
        
        try:
            # Strategy 1: Use modern Playwright locators first
            try:
                # Look for label text using get_by_text
                label_element = self.page.get_by_text(field, exact=False)
                count = await label_element.count()
                if count > 0:
                    # Try to get the input associated with this label
                    label = await label_element.first.element_handle()
                    if label:
                        # Check if it's a proper label element
                        tag_name = await self.page.evaluate("el => el.tagName.toLowerCase()", label)
                        if tag_name == "label":
                            # Get the 'for' attribute
                            for_id = await self.page.evaluate("label => label.getAttribute('for')", label)
                            if for_id:
                                # Find the input with this id
                                input_el = self.page.get_by_role("textbox", name=field)
                                input_count = await input_el.count()
                                if input_count > 0:
                                    await input_el.first.fill(text)
                                    self.logger.info(f"Filled field '{field}' using associated label")
                                    return True
                                
                else: 
                    print("Strategy 1 failed")
            except Exception as e:
                self.logger.info(f"Strategy 1 (get_by_text with label) failed: {e}")
            
            # Strategy 2: Use get_by_placeholder
            try:
                element = self.page.get_by_placeholder(field, exact=False)
                count = await element.count()
                if count > 0:
                    await element.first.fill(text)
                    self.logger.info(f"Filled field with placeholder '{field}'")
                    return True
                else: 
                    print("Strategy 2 failed")
            except Exception as e:
                self.logger.info(f"Strategy 2 (get_by_placeholder) failed: {e}")
            
            # Strategy 3: Use get_by_label
            try:
                element = self.page.get_by_label(field, exact=False)
                count = await element.count()
                if count > 0:
                    await element.first.fill(text)
                    self.logger.info(f"Filled field with label '{field}'")
                    return True
                else: 
                    print("Strategy 3 failed")
            except Exception as e:
                self.logger.info(f"Strategy 3 (get_by_label) failed: {e}")
            
            # Strategy 4: Look for input with matching placeholder
            element = await self.page.query_selector(f"input[placeholder*='{safe_field}' i]")
            if element:
                await element.fill(text)
                self.logger.info(f"Filled input with placeholder containing '{field}'")
                return True
            
            # Strategy 5: Look for input with matching name or id
            element = await self.page.query_selector(f"input[name*='{safe_field}' i], input[id*='{safe_field}' i]")
            if element:
                await element.fill(text)
                self.logger.info(f"Filled input with matching name/id containing '{field}'")
                return True
            
            # Strategy 6: Look for label with matching text and its associated input
            label = await self.page.query_selector(f"label:has-text('{safe_field}')")
            if label:
                # Get the 'for' attribute to find the input
                for_id = await self.page.evaluate("label => label.getAttribute('for')", label)
                if for_id:
                    element = await self.page.query_selector(f"#{for_id}")
                    if element:
                        await element.fill(text)
                        self.logger.info(f"Filled input associated with label '{field}' via for attribute")
                        return True
                else:
                    # Look for input inside the label
                    element = await self.page.query_selector(f"label:has-text('{safe_field}') input")
                    if element:
                        await element.fill(text)
                        self.logger.info(f"Filled input nested inside label '{field}'")
                        return True
            
            # Strategy 7: Look for textarea
            element = await self.page.query_selector(f"textarea[placeholder*='{safe_field}' i], textarea[name*='{safe_field}' i]")
            if element:
                await element.fill(text)
                self.logger.info(f"Filled textarea with placeholder/name containing '{field}'")
                return True
            
            # Strategy 8: Look for aria-label or title attributes
            element = await self.page.query_selector(f"input[aria-label*='{safe_field}' i], input[title*='{safe_field}' i]")
            if element:
                await element.fill(text)
                self.logger.info(f"Filled input with aria-label/title containing '{field}'")
                return True
            
            # Strategy 9: Look for contenteditable elements
            element = await self.page.query_selector(f"[contenteditable='true']:has-text('{safe_field}')")
            if element:
                await element.fill(text)
                self.logger.info(f"Filled contenteditable element containing '{field}'")
                return True
            
            # Strategy 10: Special handling for common login fields
            if field.lower() in ["username", "email", "password"]:
                if field.lower() in ["username", "email"]:
                    # Try standard username/email fields
                    for selector in ["input[type='text']", "input[type='email']", "input:not([type])"]:
                        element = await self.page.query_selector(selector)
                        if element:
                            await element.fill(text)
                            self.logger.info(f"Filled likely {field} field using type detection")
                            return True
                elif field.lower() == "password":
                    element = await self.page.query_selector("input[type='password']")
                    if element:
                        await element.fill(text)
                        self.logger.info("Filled password field")
                        return True
            
            # Strategy 11: If the field might contain multiple words, try to match partial text
            words = field.split()
            if len(words) > 1:
                for word in words:
                    if len(word) > 3:  # Only use words with more than 3 chars to avoid false matches
                        element = await self.page.query_selector(
                            f"input[placeholder*='{word}' i], input[name*='{word}' i], " +
                            f"input[id*='{word}' i], input[aria-label*='{word}' i]"
                        )
                        if element:
                            await element.fill(text)
                            self.logger.info(f"Filled field matching partial keyword '{word}' from '{field}'")
                            return True
            
            self.logger.error(f"Could not find field to fill: {field}")
            return False
        
        except Exception as e:
            self.logger.error(f"Error while trying to fill field '{field}': {str(e)}")
            return False
    
    async def type_text(self, text: str, delay: int = 100) -> bool:
        """
        Type text character by character using the keyboard.
        
        Args:
            text: The text to type
            delay: Delay between keystrokes in milliseconds
            
        Returns:
            True if typing was successful, False otherwise
        """
        try:
            for char in text:
                await self.page.keyboard.type(char, delay=delay)
            self.logger.info(f"Typed text: '{text}'")
            self.command_history.append(f"type_text('{text}')")
            return True
        except Exception as e:
            self.last_error = str(e)
            self.logger.error(f"Failed to type text '{text}': {e}")
            return False
       
    async def press_key(self, key: str) -> bool:
        try:
            await self.page.keyboard.press(key, delay=500)
            return True
        except Exception as e:
            self.last_error = str(e)
            self.logger.error(f"Failed to press key '{key}': {e}")
            return False