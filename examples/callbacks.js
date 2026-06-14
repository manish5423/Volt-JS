function process(arr, callback) {
    let result = [];
    for (let i = 0; i < arr.length; i++) {
        result.push(callback(arr[i]));
    }
    return result;
}

let numbers = [1, 2, 3];
let squared = process(numbers, (x) => x * x);
console.log(squared.join(", "));
