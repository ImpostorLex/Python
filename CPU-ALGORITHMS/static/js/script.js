// The DOMContentLoaded ensures that the JS will only executes after the html 
// is finished loading
// document.addEventListener('DOMContentLoaded', function () {
//     const selectBox = document.getElementById('selectBox');

//     selectBox.addEventListener('change', function (event) {
//         const selectedOption = event.target.value;
//         console.log('Selected option:', selectedOption);

//         if (selectedOption === "2") {
//             var quantumBox = document.createElement("input");
//             quantumBox.setAttribute("type", "text");
//             quantumBox.id = "quantumBox";

//             // Apply bootstrap styling
//             quantumBox.classList.add("form-control");
//             var quantumLabel = document.createElement("label");
//             quantumLabel.setAttribute("for", "quantumBox");
//             quantumLabel.innerText = "Quantum"; // Set the label text
//             quantumLabel.id = "quantumLabel";

//             document.getElementById("formContainer").appendChild(quantumLabel);
//             document.getElementById("formContainer").appendChild(quantumBox);

//         }
//         else {
//             var quantumBox = document.getElementById("quantumBox");
//             var quantumLabel = document.getElementById("quantumLabel");
//             if (quantumBox && quantumLabel) {
//                 document.getElementById("formContainer").removeChild(quantumBox);
//                 document.getElementById("formContainer").removeChild(quantumLabel);

//             }
//         }
//     });
// });


function validateInput(nums, nums1) {

    var at_time = nums.value.trim();
    var bt_time = nums1.value.trim();


    const atHasLetters = /[a-zA-Z*{}]/.test(at_time);
    const btHasLetters = /[a-zA-Z*{}]/.test(bt_time);


    return at_time.length !== bt_time.length && at_time.length === 0 && bt_time.length === 0 && atHasLetters && btHasLetters;
}

(() => {
    'use strict';

    // Fetch all the forms we want to apply custom Bootstrap validation styles to
    const forms = document.querySelectorAll('.needs-validation');

    // Loop over them and prevent submission
    Array.from(forms).forEach((form) => {
        form.addEventListener('submit', (event) => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            } else {
                const atInput = form.querySelector('#arrivalTime');
                const btInput = form.querySelector('#burstTime');

                let hasError = validateInput(atInput, btInput);
                console.log("eror")
                if (hasError) {
                    atInput.classList.add('is-invalid');
                    btInput.classList.add('is-invalid');

                } else {
                    atInput.classList.remove('is-invalid');
                    btInput.classList.remove('is-invalid');

                }


            }
        }, false);

        form.addEventListener('click', () => {
            form.classList.remove('was-validated');
        });
    });
})();


const selectBox = document.getElementById('selectBox');

selectBox.addEventListener('change', function (event) {
    const selectedOption = event.target.value;
    console.log('Selected option:', selectedOption);

    if (selectedOption === '2') {
        var quantumBox = document.createElement('input');
        quantumBox.setAttribute('type', 'text');
        quantumBox.id = 'quantumBox';

        // Apply bootstrap styling
        quantumBox.classList.add('form-control');
        var quantumLabel = document.createElement('label');
        quantumLabel.setAttribute('for', 'quantumBox');
        quantumLabel.innerText = 'Quantum'; // Set the label text
        quantumLabel.id = 'quantumLabel';

        document.getElementById('formContainer').appendChild(quantumLabel);
        document.getElementById('formContainer').appendChild(quantumBox);
    } else {
        var quantumBox = document.getElementById('quantumBox');
        var quantumLabel = document.getElementById('quantumLabel');
        if (quantumBox && quantumLabel) {
            document.getElementById('formContainer').removeChild(quantumBox);
            document.getElementById('formContainer').removeChild(quantumLabel);
        }
    }
});





