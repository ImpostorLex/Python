// The DOMContentLoaded ensures that the JS will only executes after the html 
// is finished loading
document.addEventListener('DOMContentLoaded', function () {
    const selectBox = document.getElementById('selectBox');

    selectBox.addEventListener('change', function (event) {
        const selectedOption = event.target.value;
        console.log('Selected option:', selectedOption);

        if (selectedOption === "2") {
            var quantumBox = document.createElement("input");
            quantumBox.setAttribute("type", "text");
            quantumBox.id = "quantumBox";

            // Apply bootstrap styling
            quantumBox.classList.add("form-control");
            var quantumLabel = document.createElement("label");
            quantumLabel.setAttribute("for", "quantumBox");
            quantumLabel.innerText = "Quantum"; // Set the label text
            quantumLabel.id = "quantumLabel";

            document.getElementById("formContainer").appendChild(quantumLabel);
            document.getElementById("formContainer").appendChild(quantumBox);

        }
        else {
            var quantumBox = document.getElementById("quantumBox");
            var quantumLabel = document.getElementById("quantumLabel");
            if (quantumBox && quantumLabel) {
                document.getElementById("formContainer").removeChild(quantumBox);
                document.getElementById("formContainer").removeChild(quantumLabel);

            }
        }
    });
});