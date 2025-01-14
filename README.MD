# Telegram Bot for Private Clinic

## Overview

This Telegram bot is designed to handle applications and feedback from users, and send notifications to administrators in a group chat.

## Features

### User Features
- **Commands and Buttons:**
  - `/start` — Launch the bot and display a welcome message.
  - Buttons:
    - "Оставить заявку" (Collects data: name, phone number, comment).
    - "Оставить отзыв" (Collects feedback text and rating from 1 to 5).
    - "Связаться с администратором" (Displays clinic contact information).

- **Data Collection:**
  - **For Applications:**
    - Name.
    - Phone number (manual input or auto-fill button).
    - Comment (optional).
  - **For Feedback:**
    - Rating from 1 to 5 (button selection).
    - Feedback text.

- **Confirmations:**
  - Application: "Your application has been received. Please wait for a call."
  - Feedback: "Thank you for your feedback! We value your opinion."

### Admin Features
- Receive notifications in a group chat:
  - Applications:
    ```
    New Application:
    Name: [Name]
    Phone Number: [Phone Number]
    Comment: [Comment]
    ```
  - Feedback:
    ```
    New Feedback:
    Rating: [1-5]
    Comment: [Text]
    ```

## Non-functional Requirements
- **Interface Language:** Russian.
- **Limitation:** Only one user can interact at a time.
- **Deadline:** By February 10, 2025.
- **Hosting:** Free (Heroku) or local server.

## Architecture

### Main Modules:
1. **Telegram API Interaction Module:**
   - Command and button handling.
   - Sending messages to users and administrators.

2. **Application Module:**
   - Collecting data from users.
   - Forming an application.
   - Sending the application to the admin group chat.

3. **Feedback Module:**
   - Collecting feedback (rating + text).
   - Sending feedback to the admin group chat.

4. **Confirmation Module:**
   - User messages after data submission.

## Implementation Steps

1. **Create a Telegram Bot:**
   - Register the bot via BotFather and obtain a token.

2. **Determine Admin Chat ID:**
   - Create a group chat.
   - Add the bot to it.
   - Find out the ID via @userinfobot or test message sending.

3. **Develop the Code:**
   - Use Python and the `python-telegram-bot` library.
   - Set up command and button handling.
   - Implement data collection for applications and feedback.
   - Set up message sending to the group chat.

4. **Testing:**
   - Verify data collection accuracy.
   - Ensure messages are sent to the group chat.
   - Check the user interface.

## Completion Criteria
1. The bot accepts applications (name, phone, comment) and sends them to administrators.
2. The bot accepts feedback (rating, text) and sends it to administrators.
3. The user receives confirmation after data submission.
4. The bot works stably and is user-friendly.
