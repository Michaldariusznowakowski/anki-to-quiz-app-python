from anki.collection import Collection
import os
import base64
import re
import random
# Update this variable with the name of your model if you want to use another model
MODEL_NAME = "Test by MX"


class Deck:
    def __init__(self, name, AnkiCore):
        """Initializes the Deck object.

        Args:
            name (str): Name of the deck
        """
        self.name = name
        self.AnkiCore = AnkiCore
        self.cards = []
        self.deckWithModel = False
        self.questions = []
        self.answers = []
        self.correct = []
        self.images = []
        self.index = 0
        self.score = 0
        self.wrongQuestions = []
        self.errors = []
        self.questionsNum = 0
        self.loaded = False

    def loadCard(self) -> int:
        """Loads the deck and returns the status of the loading.

        Returns:
            int: 0 if success, -1 if deck not found, -2 if no cards found
        """
        if self.name not in self.AnkiCore.decksNames:
            return -1
        # find cards in deck
        cards = self.AnkiCore.collection.find_cards(f'deck:"{self.name}"')
        # find model of cards
        for card in cards:
            model = self.AnkiCore.collection.get_card(card).note_type()['name']
            # if model is "Test by MX" add card to list
            if model == self.AnkiCore.model:
                self.cards.append(card)
        if len(self.cards) == 0:
            return -2
        if self._loadQuestions(self.name) == -1:
            return -2
        self.loaded = True
        return 0

    def shuffle(self):
        """Shuffles the current question.
        """
        if self.loaded == False:
            return

        oldAnswers = self.answers[self.index]
        oldCorrect = self.correct[self.index]

        answersWithCorrect = []
        for i in range(len(oldAnswers)):
            if i in oldCorrect:
                answersWithCorrect.append([oldAnswers[i], True])
            else:
                answersWithCorrect.append([oldAnswers[i], False])

        random.shuffle(answersWithCorrect)

        newAnswers = [answersWithCorrect[i][0]
                      for i in range(len(answersWithCorrect))]
        newCorrect = []
        for i in range(len(answersWithCorrect)):
            if answersWithCorrect[i][1] == True:
                newCorrect.append(i)

        self.answers[self.index] = newAnswers
        self.correct[self.index] = newCorrect

    def nextQuestion(self):
        """Returns the next question and the status of the loading.
        Returns:
            int: 0 if success, -1 if no more questions, -2 if deck not loaded
        """
        if self.index >= self.questionsNum-1:
            return -1
        if self.loaded == False:
            return -2
        self.index += 1
        return 0

    def getErrors(self) -> list:
        """Returns the errors.

        Returns:
            list: Errors
        """
        return self.errors

    def getQuestion(self) -> str:
        """Returns the question.

        Returns:
            str: Question
            str: "" if no more questions or deck not loaded
        """
        if self.index >= self.questionsNum:
            return ""
        if self.loaded == False:
            return ""
        return self.questions[self.index],

    def getAnswers(self) -> list:
        """Returns the answers.

        Returns:
            list: Answers
            list: [] if no more questions or deck not loaded
        """
        if self.index >= self.questionsNum:
            return []
        if self.loaded == False:
            return []
        return self.answers[self.index]

    def getImages(self) -> list:
        """Returns the images.

        Returns:
            list: Images
            list: [] if no more questions or deck not loaded
        """
        if self.index >= self.questionsNum:
            return []
        if self.loaded == False:
            return []
        return self.images[self.index]

    def updateScore(self, answers) -> int:
        if self.loaded == False:
            return -1
        if self.index >= self.questionsNum:
            return -2
        point = False
        for answer in answers:
            if answer not in self.correct[self.index]:
                point = False
                break
            if answer in self.correct[self.index]:
                point = True
        if point == True:
            self.score += 1
        else:
            self.wrongQuestions.append(self.questions[self.index])
        return 0

    def getScore(self) -> int:
        """Returns the score.

        Returns:
            int: Score
        """
        return self.score

    def getMaxScore(self) -> int:
        """Returns the maximum score.

        Returns:
            int: Maximum score
        """
        return self.questionsNum

    def getScorePercentage(self) -> float:
        """Returns the score percentage.

        Returns:
            float: Score percentage
        """
        return round(self.score/self.questionsNum*100, 2)

    def getWrongQuestions(self) -> list:
        """Returns the wrong questions.

        Returns:
            list: Wrong questions
        """
        return self.wrongQuestions

    def getDeckName(self) -> str:
        """Returns the deck name.

        Returns:
            str: Deck name
        """
        return self.name

    def getQuestionsNum(self) -> int:
        """Returns the number of questions.

        Returns:
            int: Number of questions
        """
        return self.questionsNum

    def getQuestionIndex(self) -> int:
        """Returns the index of the question.

        Returns:
            int: Index of the question
        """
        return self.index

    def isLoaded(self) -> bool:
        """Returns the status of the loading.

        Returns:
            bool: True if loaded, False if not loaded
        """
        return self.loaded

    def _loadQuestions(self, deckName) -> int:
        """Loads the questions and returns the status of the loading.

        Returns:
            int:  0 if success, -1 if no cards found
        """
        questions = []
        answers = []
        correct = []
        images = []
        errors = []
        for card in self.cards:
            note = self.AnkiCore.collection.get_card(card).note()
            fields_num = len(note.fields)
            question = note.fields[0]
            [question, imgsrc] = self.findImages(question)
            answer = note.fields[1:fields_num-1]
            answer = [x for x in answer if x != ""]
            correct = note.fields[fields_num-1]
            imgbase64 = self._getImage64(imgsrc)
            if (len(correct) == 0) or (len(answer) == 0) or (len(question) == 0):
                if len(question) != 0:
                    errors.append(question)
                else:
                    errors.append("Unknown, cannot show question")
                continue
            self.correct.append(self._correctToIndex(correct))
            self.questions.append(self._clearString(question))
            self.answers.append(self._clearString(answer))
            self.images.append(imgbase64)
        self.questionsNum = len(self.questions)
        if len(self.questions) == 0:
            return -1
        return 0

    def _clearString(self, string) -> str:
        """Clears the string from HTML tags and returns the cleared string.

        Args:
            string (str): String to clear

        Returns:
            str: Cleared string
        """
        if isinstance(string, list):
            for i in range(len(string)):
                string[i] = self._clearString(string[i])
            return string

        string = string.replace("<br>", "\n")
        string = string.replace("<br/>", "\n")
        string = string.replace("<br />", "\n")
        string = string.replace("<br >", "\n")
        string = string.replace("&nbsp;", " ")
        string = string.replace("&lt;", "<")
        string = string.replace("&gt;", ">")
        string = string.replace("&amp;", "&")
        string = string.replace("&quot;", "\"")
        string = string.replace("&apos;", "'")
        string = string.replace("&cent;", "¢")
        string = string.replace("&pound;", "£")
        string = string.replace("&yen;", "¥")
        string = string.replace("&euro;", "€")
        string = string.replace("&copy;", "©")
        string = string.replace("&reg;", "®")
        string = string.replace("&trade;", "™")
        string = string.replace("&times;", "×")
        string = string.replace("&divide;", "÷")
        string = string.replace("&ndash;", "–")
        string = string.replace("&mdash;", "—")
        string = string.replace("&lsquo;", "‘")
        string = string.replace("&rsquo;", "’")
        string = string.replace("&sbquo;", "‚")
        string = string.replace("&ldquo;", "“")
        string = string.replace("&rdquo;", "”")
        string = string.replace("&bdquo;", "„")
        string = string.replace("&laquo;", "«")
        string = string.replace("&raquo;", "»")
        return string

    def _correctToIndex(self, correct) -> list:
        """Converts the correct answer to an index.
            Args:
                correct (str): Correct answer
            Returns:
                list: List of index
        """
        # Correct input is for example "ABCgEf"
        correct = correct.upper()
        correct = correct.replace(" ", "")
        correctExploded = list(correct)
        correctIndex = []
        for letter in correctExploded:
            correctIndex.append(ord(letter)-65)
        return correctIndex

    def _getImage64(self, images) -> list:
        """Loads and adds the images to the question.

        Args:
            images (list): List of images
        Returns:
            list: List of images in base64
        """
        srcs = []
        # find image in anki
        for image in images:
            # find image in anki
            directory = self.AnkiCore.collection.media.dir()
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith(image):
                        srcs.append(os.path.join(root, file))

        # load images and change them to base64
        images64 = []
        for src in srcs:
            with open(src, 'rb') as f:
                data = f.read()
            images64.append(base64.b64encode(data).decode('utf-8'))
        if len(images64) == 0:
            return [None]
        return images64

    def findImages(self, question) -> list:
        """Finds the images in the questions and returns the status of the finding.

        Returns:
            list: [question, images]
        """
        images = []
        # find images in question
        pattern = r'<img src="([^"]+)"'
        for match in re.finditer(pattern, question):
            images.append(match.group(1))

        question = self.AnkiCore.collection.media.strip(question)
        return [question, images]


class AnkiCore:
    def __init__(self, model=MODEL_NAME):
        """Initializes the AnkiCore object.

        Args:
            model (_type_, optional): Model name. Defaults to MODEL_NAME.
        """
        self.model = model
        self.collection = None
        self.decksNames = None
        self.decksWithModel = None
        self.init = False

    def Init(self) -> int:
        """Initializes the AnkiCore object and returns the status of the initialization.

        Returns:
            int: 0 if success, -1 if path not found, -2 if collection not found, -3 if error while opening collection, -4 if no decks found
        """
        out = self._connectAnkiDB()
        if out == 0:
            self.init = True
        if self._loadSupportedDecks() == -2:
            out = -4
        return out

    def getDecksNames(self) -> list:
        """Returns the decks names.

        Returns:
            list: Decks names
        """
        return self.decksNames

    def getDeck(self, deckName) -> Deck:
        """Returns the deck.

        Args:
            deckName (str): Deck name

        Returns:
            Deck: Deck
        """
        return Deck(deckName, self)

    def _loadSupportedDecks(self) -> int:
        """Loads the supported decks and returns the status of the loading.

        Returns:
            int: -1 if AnkiCore is not initialized, 0 if success, -2 if no decks found
        """
        if self.init == False:
            return -1
        decks = self.collection.decks.all()
        decks_with_model = []
        for deck in decks:
            # find cards in deck
            cards = self.collection.find_cards(f'deck:"{deck["name"]}"')
            # find model of cards
            for card in cards:
                model = self.collection.get_card(card).note_type()['name']
                # if model is "Test by MX" add deck to list
                if model == self.model:
                    decks_with_model.append(deck)
                    break
        if len(decks_with_model) == 0:
            return -2
        # create list of decks names
        decks_names = [deck['name'] for deck in decks_with_model]
        self.decksWithModel = decks_with_model
        self.decksNames = decks_names
        return 0

    def _connectAnkiDB(self) -> int:
        """Connects to the Anki database and returns the status of the connection.

        Returns:
            int: 0 if success, -1 if path not found, -2 if collection not found, -3 if error while opening collection
        """
        path = self._getAnkiPath()
        if path == None:
            return -1

        # Find collection.anki2
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith('collection.anki2'):
                    collection_path = os.path.join(root, file)
                    break

        # If collection.anki2 not found
        if collection_path == '':
            return -2

        # Open collection.anki2
        try:
            self.collection = Collection(collection_path)
        except:
            # Error while opening collection.anki2
            return -3

        # Collection.anki2 opened successfully
        return 0

    def _getAnkiPath(self) -> str:
        """Returns the path of the Anki folder.

        Returns:
            str: Path of the Anki folder
            str: None if the OS is not supported
        """
        if os.name == 'nt':
            return self._getWindowsAnkiPath()
        elif os.name == 'posix':
            return self._getLinuxAnkiPath()
        elif os.name == 'darwin':
            return self._getMacOSAnkiPath()
        else:
            return None

    def _getMacOSAnkiPath(self) -> str:
        """Returns the path of the Anki folder on MacOS.

        Returns:
            str: Path of the Anki folder on MacOS
        """
        return os.path.join(os.getenv('HOME'), 'Documents/Anki')

    def _getWindowsAnkiPath(self) -> str:
        """Returns the path of the Anki folder on Windows.

        Returns:
            str: Path of the Anki folder on Windows
        """
        return os.path.join(os.getenv('APPDATA'), 'Anki2')

    def _getLinuxAnkiPath(self) -> str:
        """Returns the path of the Anki folder on Linux.

        Returns:
            str: Path of the Anki folder on Linux
        """
        return os.path.join(os.getenv('HOME'), '.local/share/Anki2')
