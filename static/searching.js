const DEFAULT_COLOR = '#007BFF';
const COMPARE_COLOR = '#FF5733';
const FOUND_COLOR = '#28A745';
const NOT_FOUND_COLOR = '#DC3545';

let array = [];
let searching = false;

const linearSearchCode = `function linearSearch(arr, target) {
    for (let i = 0; i < arr.length; i++) {
        if (arr[i] === target) {
            return i;
        }
    }
    return -1;
}`;

const binarySearchCode = `function binarySearch(arr, target) {
    let left = 0;
    let right = arr.length - 1;
    while (left <= right) {
        let mid = Math.floor((left + right) / 2);
        if (arr[mid] === target) return mid;
        else if (arr[mid] < target) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}`;

function generateRandomArray() {
    array = [];
    for (let i = 0; i < 20; i++) {
        array.push(Math.floor(Math.random() * 100) + 1);
    }
    displayArray();
    displayCode(document.getElementById("searchSelect").value);
}

function generateSortedRandomArray() {
    array = [];
    for (let i = 0; i < 20; i++) {
        array.push(Math.floor(Math.random() * 100) + 1);
    }
    array.sort((a, b) => a - b);
    displayArray();
    displayCode(document.getElementById("searchSelect").value);
}

function takeUserInput() {
    const userInput = document.getElementById("userArrayInput").value;
    if (userInput) {
        array = userInput.split(",").map(num => parseInt(num.trim(), 10)).filter(num => !isNaN(num));
        displayArray();
        displayCode(document.getElementById("searchSelect").value);
    }
}

function displayArray(highlightIndices = [], color = COMPARE_COLOR) {
    const arrayContainer = document.getElementById("arrayContainer");
    arrayContainer.innerHTML = '';
    array.forEach((num, idx) => {
        const bar = document.createElement("div");
        bar.classList.add("bar");
        bar.style.height = `${num * 4}px`;
        bar.textContent = num;

        if (highlightIndices.includes(idx)) {
            bar.style.backgroundColor = color;
        } else {
            bar.style.backgroundColor = DEFAULT_COLOR;
        }
        
        arrayContainer.appendChild(bar);
    });
}

function displayCode(algorithm) {
    const codeDisplay = document.getElementById("codeDisplay");
    if (algorithm === 'linear') {
        codeDisplay.textContent = linearSearchCode;
    } else if (algorithm === 'binary') {
        codeDisplay.textContent = binarySearchCode;
    } else {
        codeDisplay.textContent = "// Code not available for the selected algorithm.";
    }
    hljs.highlightElement(codeDisplay);
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function startSearch() {
    if (searching) return;
    searching = true;
    const algorithm = document.getElementById("searchSelect").value;
    const speed = document.getElementById("speedSelect").value;
    let speedFactor = 250;

    if (speed === 'fast') speedFactor = 100;
    else if (speed === 'slow') speedFactor = 400;

    const targetInput = document.getElementById("searchInput").value;

    if (targetInput === '') {
        alert("Please enter a number to search.");
        searching = false;
        return;
    }

    let target = parseInt(targetInput, 10);

    if (isNaN(target)) {
        alert("Please enter a valid number.");
        searching = false;
        return;
    }

    if (algorithm === 'binary') {
        if (!isSorted(array)) {
            alert("The array must be sorted to execute binary search.");
            searching = false;
            return;
        }
    }

    const response = await mockSearch(array, target, algorithm);

    if (response.error) {
        alert(response.error);
        searching = false;
        return;
    }

    for (let i = 0; i < response.steps.length; i++) {
        const step = response.steps[i];
        array = step.array;
        displayArray(step.indices, COMPARE_COLOR);
        await sleep(speedFactor);

        if (response.found && i === response.steps.length - 1) {
            displayArray([response.index], FOUND_COLOR);
            await sleep(speedFactor);
        }
    }

    if (!response.found) {
        await sleep(speedFactor);
        alert("Element not found in the array.");
    }

    searching = false;
}

function isSorted(arr) {
    return arr.every((val, i, array) => !i || array[i - 1] <= val) ||
           arr.every((val, i, array) => !i || array[i - 1] >= val);
}

async function mockSearch(array, target, algorithm) {
    const steps = [];
    let foundIndex = -1;

    if (algorithm === 'linear') {
        for (let i = 0; i < array.length; i++) {
            steps.push({ array: [...array], indices: [i] });
            if (array[i] === target) {
                foundIndex = i;
                break;
            }
            await sleep(50);
        }
    } else if (algorithm === 'binary') {
        let left = 0;
        let right = array.length - 1;
        while (left <= right) {
            let mid = Math.floor((left + right) / 2);
            steps.push({ array: [...array], indices: [mid] });
            if (array[mid] === target) {
                foundIndex = mid;
                break;
            } else if (array[mid] < target) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
            await sleep(50); 
        }
    }

    if (foundIndex === -1) {
        return { steps, found: false };
    } else {
        return { steps, found: true, index: foundIndex };
    }
}

function generateArray() {
    const algorithm = document.getElementById("searchSelect").value;
    if (algorithm === 'binary') {
        generateSortedRandomArray();
    } else {
        generateRandomArray();
    }
}

document.getElementById("searchSelect").addEventListener("change", function() {
    const selectedAlgorithm = this.value;
    displayCode(selectedAlgorithm);
    generateArray();
});

generateArray();