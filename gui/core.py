from ankidata import core as ankidata
from docxsave import core as docxsave
import customtkinter as tk
from customtkinter import filedialog
import io
import base64
import PIL.Image
import PIL.ImageTk


class Gui:
    def __init__(self):
        tk.set_widget_scaling(1.5)
        self.deck = None
        self.test_options = None
        self.tests_list = None
        self.test_view = None
        self.test_view_score = None
        self.text_export = None
        self.error_prompt = None
        self.checkboxes = []

        tk.set_appearance_mode("Dark")
        self.window = tk.CTk()
        self.window.title("AnkiTest")
        self.window.geometry("800x600")
        self.window.resizable(True, True)

        self.anki = ankidata.AnkiCore()
        status = self.anki.Init()
        if status == -1:
            self.showError("Path to Anki not found")
            return
        if status == -2:
            self.showError("Cannot find Anki database")
            return
        if status == -3:
            self.showError("Close Anki before running this program")
            return

        self.testList()

        self.window.mainloop()

    def testList(self):
        self.refreshView()
        self.tests_list = tk.CTkScrollableFrame(
            self.window, width=800, height=600, label_anchor="n", label_text="Tests", label_font=("Arial", 20))
        self.tests_list.pack(side="left", fill="both", expand=True)
        tests = self.anki.getDecksNames()
        for test in tests:
            tk.CTkButton(self.tests_list, text=test, command=lambda test=test: self.showTestOptions(
                test)).pack(side="top", fill="both", expand=True, pady=5)

    def showTestOptions(self, test):
        self.refreshView()
        self.deck = self.anki.getDeck(test)
        self.test_options = tk.CTkScrollableFrame(
            self.window, width=800, height=600, label_anchor="n", label_text="Test Options", label_font=("Arial", 20))
        self.test_options.pack(side="left", fill="both", expand=True)
        tk.CTkButton(self.test_options, text="Back to Test Selection", text_color="black",
                     command=lambda: self.testList()).pack(side="left", fill="both", expand=True, pady=5)
        start_test_button = tk.CTkButton(
            self.test_options, text="Start Test", command=lambda: self.startTest(test))
        start_test_button.pack(side="left", fill="both", expand=True, pady=5)

        export_button = tk.CTkButton(
            self.test_options, text="Export to File", command=lambda: self.exportToFile(test))
        export_button.pack(side="left", fill="both", expand=True, pady=5)

    def startTest(self, test):
        self._hideTestOptions()
        self.deck = self.anki.getDeck(test)
        self.deck.loadCard()
        self.updateTestView()

    def refreshView(self):
        self._hideTestView()
        self._hideTestViewScore()
        self._hideTestOptions()
        self._hideScoreScreen()
        self._hideTestList()
        self.window.update()

    def _hideTestList(self):
        if self.tests_list == None:
            return
        self.tests_list.pack_forget()
        self.tests_list.destroy()
        self.tests_list = None

    def _hideTestOptions(self):
        if self.test_options == None:
            return
        self.test_options.pack_forget()
        self.test_options.destroy()
        self.test_options = None

    def _hideTestViewScore(self):
        if self.test_view_score != None:
            self.test_view_score.pack_forget()
            self.test_view_score.destroy()
            self.test_view_score = None

    def _hideTestView(self):
        if self.test_view != None:
            self.test_view.pack_forget()
            self.test_view.destroy()
            self.test_view = None
            self.checkboxes = []

    def _hideScoreScreen(self):
        if self.test_view_score == None:
            return
        self.test_view_score.pack_forget()
        self.test_view_score.destroy()
        self.test_view_score = None

    def updateTestView(self):
        self.refreshView()
        self.deck.shuffle()
        self.test_view = tk.CTkScrollableFrame(
            self.window, width=800, height=600, label_anchor="n", label_text=self.deck.getDeckName(), label_font=("Arial", 20))
        self.test_view.pack(side="left", fill="both", expand=True)
        tk.CTkButton(self.test_view, text="Back to Test Selection", width=3, height=1,
                     command=lambda: self.testList(
                     )).pack(side="top", pady=3)
        question = self.deck.getQuestion()
        if question == None:
            self.refreshView()
            self.showError("No questions found")
            self.testList()
            return
        if isinstance(question, tuple):
            question = str(question[0])
        images = self.deck.getImages()
        answers = self.deck.getAnswers()
        if answers == None or len(answers) == 0:
            self.refreshView()
            self.showError("No answers found")
            self.testList()
            return

        tk.CTkLabel(self.test_view, text=str(self.deck.getQuestionIndex()+1)+"/"+str(
            self.deck.getQuestionsNum())+" Question:").pack(side="top", fill="x", expand=True)
        tk.CTkLabel(self.test_view, text=question, wraplength=500).pack(
            side="top", fill="x", expand=True)
        if images != None:
            for image in images:
                if image == None or image == "":
                    continue
                decoded_string = io.BytesIO(base64.b64decode(image))
                img = PIL.Image.open(decoded_string)
                width, height = img.size
                if width > 500:
                    height = int(height*(500/width))
                    width = 500

                imgToDisp = tk.CTkImage(img, size=(width, height))

                tk.CTkLabel(self.test_view, image=imgToDisp, text="").pack(
                    side="top", fill="x", expand=True)

        self.checkboxes = []
        for answer in answers:
            self.checkboxes.append(tk.IntVar())
            tk.IntVar().get()
            tk.CTkCheckBox(self.test_view, text=answer, variable=self.checkboxes[-1], onvalue=1, offvalue=0
                           ).pack(side="top", fill="x", expand=True)
            # a the bottom of the test view
        tk.CTkButton(self.test_view, text="Next Question", command=lambda: self.nextQuestion(
        )).pack(side="bottom", fill="both", expand=True, pady=5)

    def nextQuestion(self):
        selected = []
        for i in range(len(self.checkboxes)):
            if self.checkboxes[i].get() == 1:
                selected.append(i)
        self.deck.updateScore(selected)
        status = self.deck.nextQuestion()
        if status == -2:
            self.refreshView
            self.showError("Deck is not loaded? WTF")
            self.testList()
            return
        if status == -1:
            self.showScoreScreen()
            return
        self.updateTestView()

    def exportToFile(self, test):
        # windows screen with save file dialog
        # save file dialog
        path = filedialog.asksaveasfilename(defaultextension=".docx", filetypes=(
            ("Word Document", "*.docx"), ("All Files", "*.*")))
        if path == "":
            self.showError("No file selected")
            self.testList()
            return
        exp = docxsave.exportAnki(path)

        self.deck = self.anki.getDeck(test)
        status = self.deck.loadCard()
        if status == -1:
            self.showError("Deck not found")
            self.testList()
            return
        if status == -2:
            self.showError("Deck is empty")
            self.testList()
            return
        if status == -3:
            self.showError("Deck is not loaded")
            self.testList()
            return
        questions = self.deck.questions
        answers = self.deck.answers
        correct = self.deck.correct
        images = self.deck.images
        deckName = self.deck.getDeckName()
        if len(questions) == 0:
            self.showError("No questions found")
            self.testList()
            return

        exp.export(questions, answers, correct, deckName, images)
        self.testList()

    def showScoreScreen(self):
        self.refreshView()
        self.test_view_score = tk.CTkScrollableFrame(
            self.window, width=800, height=600, label_anchor="n", label_text="Score", label_font=("Arial", 20))
        tk.CTkButton(self.test_view_score, text="Back to Test Selection", width=3, height=1,
                     command=lambda: self.testList(
                     )).pack(side="top", fill="both", expand=True, pady=5)
        self.test_view_score.pack(side="left", fill="both", expand=True)

        score = self.deck.getScore()
        max = self.deck.getMaxScore()
        score_precent = self.deck.getScorePercentage()
        wrongAnswers = self.deck.getWrongQuestions()
        tk.CTkLabel(self.test_view_score, text="Score: "+str(score)+"/"+str(max) +
                    " ("+str(score_precent)+"%)").pack(side="top", fill="x", expand=True)
        bar = tk.CTkProgressBar(self.test_view_score)
        bar.pack(side="top", fill="x", expand=True)
        bar.configure(width=800, height=50)
        bar.set(score/max)
        counter = 1
        tk.CTkLabel(self.test_view_score, text="Wrong answers:", font=("Arial", 20), text_color="red"
                    ).pack(
            side="top", fill="x", expand=True)
        for wrong in wrongAnswers:
            tk.CTkLabel(self.test_view_score, text=str(counter)+" "+wrong, wraplength=300).pack(
                side="top", fill="x", expand=True)
            tk.CTkLabel(self.test_view_score, text="_"*100).pack(
                side="top", fill="x", expand=True)
            counter += 1

    def showError(self, error_message):
        self._hideError(self.error_prompt)
        self.error_prompt = tk.CTkFrame(
            self.window, width=50, height=100, fg_color="red")
        self.error_prompt.pack(side="top", fill="x", expand=True)
        tk.CTkLabel(self.error_prompt, text=error_message).pack(
            side="left", fill="x", expand=True, pady=1)
        tk.CTkButton(self.error_prompt, text="Close", command=lambda: self._hideError(
            self.error_prompt), fg_color="yellow").pack(side="left", fill="x", expand=True, pady=1)

    def _hideError(self, error_prompt):
        if error_prompt == None:
            return
        error_prompt.pack_forget()
        error_prompt.destroy()
        error_prompt = None
