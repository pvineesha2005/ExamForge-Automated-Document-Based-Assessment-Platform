let timeRemaining = 30 * 60;

const timerElement = document.getElementById("timer");

const submitExam = () => {
    alert("Time is over. Exam submitted.");
};

const updateTimer = () => {

    const minutes = Math.floor(timeRemaining / 60);

    const seconds = timeRemaining % 60;

    timerElement.textContent =
        `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;

    if (timeRemaining <= 0) {
        clearInterval(timerInterval);
        submitExam();
        return;
    }

    timeRemaining--;
};

const timerInterval = setInterval(updateTimer, 1000);

updateTimer();