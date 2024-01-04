from telegram import Update, ReplyKeyboardMarkup, Poll
from telegram.ext import filters, Updater, ContextTypes, CommandHandler, ApplicationBuilder, MessageHandler, ConversationHandler

Users = []
botToken = "6441621381:AAHAcXtQqkhF4sCv9jBx3V9993Lp-zbS7oc"

WRITTING = range(1)

def AddUser(user):
    found = False
    for u in Users:
        if user.id == u['id']:
            found = True
            break

    if not found:
        NewUser = {'id': user.id, 
                    'name': user.first_name,
                    'questions': [],
                    'answers': []
                    }
        Users.append(NewUser)

def updateUserData(user, key, value):
    found = False
    for u in Users:
        if user.id == u['id']:
            found = True
            if key == "Q":
                u['questions'] = value
            elif key == "A":
                u['answers'] = value
            break

    if not found:
        AddUser(user)
        updateUserData(user, data)

async def Start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    AddUser(user)
    await update.message.reply_text("Hello, {}\nPlease enter the questions and answers in separate messages like the follwing format".format(user.first_name))
    await update.message.reply_text("#QUESTIONS\nFirst question text here\nChoice 1\nChoice 2\nChoice 3\nChoice ...\n\nSecond question text here\nChoice 1\nChoice 2\nChoice 3")
    await update.message.reply_text("#ANSWERS\nFirst answer no/letter here\nSecond answer no/letter here")
    await update.message.reply_text("Note: to add more questions or answers to the previously added ones\nreplace the hashtages with #ADD_QUESTIONS or #ADD_ANSWERS")
    
    return WRITTING

async def ReceiveData(update, context):
    user = update.effective_user
    userinput = update.message.text
    if userinput.split("\n")[0] == "#QUESTIONS":
        t = userinput.split("\n")[1:]
        text = "\n".join(t)
        questions = text.split("\n\n")
        answers = []
        updateUserData(user, "A", answers)
        for q in range(len(questions)):
            qPieces = questions[q].split("\n")
            if len(qPieces) <= 2:
                questions = []
                updateUserData(user, "Q", questions)
                await update.message.reply_text("Invalid format in question no.{}\nPlease re-enter the questions".format(q))
                break
        if len(questions) >= 1:
            updateUserData(user, "Q", questions)
            await update.message.reply_text("Questions added successfully")
    elif userinput.split("\n")[0] == "#ADD_QUESTIONS":
        t = userinput.split("\n")[1:]
        text = "\n".join(t)
        questions = text.split("\n\n")
        for q in range(len(questions)):
            qPieces = questions[q].split("\n")
            if len(qPieces) <= 2:
                questions = []
                await update.message.reply_text("Invalid format in question no.{}\nPlease re-enter the questions".format(q))
                break
        if len(questions) >= 1:
            TotalQuestions = []
            for u in Users:
                if u['id'] == user.id:
                    TotalQuestions = u['questions']
                    break
            TotalQuestions += questions
            updateUserData(user, "Q", TotalQuestions)
            await update.message.reply_text("Questions added successfully")

    elif userinput.split("\n")[0] == "#ANSWERS":
        answers = userinput.split("\n")[1:]
        newAnswers = []
        for x in answers:
            if x[len(x)-1] != "":
                target = x[len(x)-1]
                try:
                    target = int(target) - 1
                except:
                    target = target.lower()
                    if target == "a":target=0
                    elif target == "b":target=1
                    elif target == "c":target=2
                    elif target == "d":target=3
                    elif target == "e":target=4
                    elif target == "f":target=5
                    elif target == "g":target=6
                newAnswers.append(target)
            else:
                await update.message.reply_text("Invalid answers format")
                newAnswers = []
                break
        answers = newAnswers
        updateUserData(user, "A", answers)
        if len(answers) >= 1:
            await update.message.reply_text("Answers added successfully")
    elif userinput.split("\n")[0] == "#ADD_ANSWERS":
        answers = userinput.split("\n")[1:]
        newAnswers = []
        for x in answers:
            if x[len(x)-1] != "":
                target = x[len(x)-1]
                try:
                    target = int(target) - 1
                except:
                    target = target.lower()
                    if target == "a":target=0
                    elif target == "b":target=1
                    elif target == "c":target=2
                    elif target == "d":target=3
                    elif target == "e":target=4
                    elif target == "f":target=5
                    elif target == "g":target=6
                newAnswers.append(target)
            else:
                await update.message.reply_text("Invalid answers format")
                newAnswers = []
                break
        answers = newAnswers
        if len(answers) >= 1:
            TotalAnswers = []
            for u in Users:
               if u['id'] == user.id:
                   TotalAnswers = u['answers']
                   break
            TotalAnswers += answers
            updateUserData(user, "A", TotalAnswers)
            await update.message.reply_text("Answers added successfully")
            
    else:
        await update.message.reply_text("please identify if your message contains the questions or the answers by placing #QUESTIONS or #ANSWERS in the first line of your message")

async def GenerateQuiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user

    for u in Users:
        if u['id'] == user.id:
            if u['questions'] != [] and u['answers'] != []:
                if len(u['questions']) == len(u['answers']):
                    for q in range(len(u['questions'])):
                        qPieces = u['questions'][q].split("\n")
                        qText = qPieces[0]
                        qChoices = qPieces[1:]
                        qAnswer = int(u['answers'][q])

                        await update.effective_message.reply_poll(qText, 
                            qChoices,
                            type=Poll.QUIZ,
                            is_anonymous=True,
                            correct_option_id=qAnswer)
                else:
                    await update.message.reply_text("the number of answers isn't equal to that of questions")
            else:
                await update.message.reply_text("Please enter both the questions and the answers")
            break

async def Cancel(update: Update,  context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Conversation canceled\nsend /start to run it again")
    return WRITTING

bot = ApplicationBuilder().token(botToken).build()

conv_handler = ConversationHandler(
        entry_points=[CommandHandler(["start", "menu"], Start)],
        states={
            WRITTING: [
                CommandHandler(["start", "menu"], Start),
                MessageHandler(filters.TEXT & ~filters.COMMAND, ReceiveData),
                CommandHandler(["generate"], GenerateQuiz)
                ]
        },
        fallbacks=[CommandHandler('cancel', Cancel)])

bot.add_handler(conv_handler)

bot.run_polling()
