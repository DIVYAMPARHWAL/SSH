let array = [];
let sorting = false;

function generateArray() {
    array = [];
    for (let i = 0; i < 20; i++) {
        array.push(Math.floor(Math.random() * 100) + 1);
    }
    displayArray();
}

function takeUserInput() {
    const userInput = document.getElementById("userInput").value;
    if (userInput) {
        array = userInput.split(",").map(num => parseInt(num.trim(), 10));
        displayArray();
    } else {
        alert("Please enter numbers separated by commas.");
    }
}

function displayArray() {
    const arrayContainer = document.getElementById("arrayContainer");
    arrayContainer.innerHTML = '';
    array.forEach((num) => {
        const bar = document.createElement("div");
        bar.classList.add("bar");
        bar.style.height = `${num * 4}px`;
        bar.textContent = num;
        arrayContainer.appendChild(bar);
    });
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function displayAlgorithmCode() {
    const algorithm = document.getElementById("sortSelect").value;
    const codeContainer = document.getElementById("algorithmCode");
    
    if (codeSnippets[algorithm]) {
        codeContainer.textContent = codeSnippets[algorithm];
    } else {
        codeContainer.textContent = "// Algorithm code not available.";
    }
    hljs.highlightElement(codeContainer);
}

async function startSort() {
    if (sorting) return;
    sorting = true;

    displayAlgorithmCode();

    const algorithm = document.getElementById("sortSelect").value;
    const ascending = document.getElementById("orderSelect").value === 'ascending';
    const speed = document.getElementById("speedSelect").value;
    let speedFactor = 150;
    if (speed === 'fast') speedFactor = 100;
    else if (speed === 'medium') speedFactor = 250;
    else if (speed === 'slow') speedFactor = 400;

    const response = await fetch('/sort', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ array, algorithm, ascending })
    });

    const data = await response.json();

    if (data.error) {
        alert(data.error);
        sorting = false;
        return;
    }

    for (const step of data.steps) {
        array = step[0];
        displayArray();
        if (step[1] && step[1].length > 0) {
            const bars = document.getElementsByClassName("bar");
            step[1].forEach(idx => {
                if (bars[idx]) {
                    bars[idx].style.backgroundColor = 'red';
                }
            });
            await sleep(speedFactor);
            step[1].forEach(idx => {
                if (bars[idx]) {
                    bars[idx].style.backgroundColor = '#007BFF';
                }
            });
        } else {
            await sleep(speedFactor);
        }
    }
    sorting = false;
}

generateArray();
displayAlgorithmCode();