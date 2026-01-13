document.addEventListener('DOMContentLoaded', function () {
    console.log("Inventory Filter Script Loaded");

    const cars = document.querySelectorAll('.car-block-four');
    const makeInputs = document.querySelectorAll('input[name="make"]');
    const modelInputs = document.querySelectorAll('input[name="model"]');
    const minYearInputs = document.querySelectorAll('input[name="min_year"]');
    const maxYearInputs = document.querySelectorAll('input[name="max_year"]');
    const maxPriceInputs = document.querySelectorAll('input[name="max_price"]');
    const bodyTypeCheckboxes = document.querySelectorAll('input[name="body_type"]');

    // Helper to get value from a node list of inputs (for multiple Make/Model inputs on page)
    function getValue(nodeList) {
        for (let input of nodeList) {
            // Trim and check for non-empty value
            if (input.value && input.value !== 'undefined' && input.value.trim() !== '') {
                return input.value.toLowerCase();
            }
        }
        return '';
    }

    // Main Filter Function
    function filterCars() {
        // Get active filter values
        const selectedMake = getValue(makeInputs);
        const selectedModel = getValue(modelInputs);

        // Parse numerical values safely
        const minYearVal = getValue(minYearInputs);
        const maxYearVal = getValue(maxYearInputs);
        const maxPriceVal = getValue(maxPriceInputs);

        const minYear = parseInt(minYearVal) || 0;
        const maxYear = parseInt(maxYearVal) || 9999;
        const maxPrice = parseInt(maxPriceVal) || 999999;

        const selectedBodyTypes = Array.from(bodyTypeCheckboxes)
            .filter(cb => cb.checked)
            .map(cb => cb.value.toLowerCase());

        console.log("Filtering with:", { selectedMake, selectedModel, minYear, maxYear, maxPrice, selectedBodyTypes });

        let visibleCount = 0;

        cars.forEach(car => {
            const carMake = (car.dataset.make || '').toLowerCase();
            const carModel = (car.dataset.model || '').toLowerCase();
            const carYear = parseInt(car.dataset.year) || 0;
            const carPrice = parseInt(car.dataset.price) || 0;
            const carBody = (car.dataset.body || '').toLowerCase();

            let isVisible = true;

            // Make Filter
            if (selectedMake && carMake !== selectedMake) isVisible = false;

            // Model Filter
            if (selectedModel && carModel !== selectedModel) isVisible = false;

            // Year Filter
            if (carYear < minYear || carYear > maxYear) isVisible = false;

            // Price Filter
            if (carPrice > maxPrice) isVisible = false;

            // Body Type Filter (if any are selected, match one of them)
            if (selectedBodyTypes.length > 0 && !selectedBodyTypes.includes(carBody)) isVisible = false;

            // Toggle Visibility
            if (isVisible) {
                car.style.display = 'block';
                visibleCount++;
            } else {
                car.style.display = 'none';
            }
        });

        // Update result count if element exists
        const countDisplay = document.querySelector('.text-box .text');
        if (countDisplay) {
            countDisplay.innerText = `Showing ${visibleCount} vehicles`;
        }
    }

    // Attach Listeners

    // For custom dropdowns, we need to listen to the LI click because the input value is updated programmatically
    document.querySelectorAll('.dropdown li').forEach(item => {
        item.addEventListener('click', function () {
            // Updating the hidden input is handled by main.js or previous inline script
            // We wait a tiny bit to ensure the input is updated, then filter
            setTimeout(filterCars, 50);
        });
    });

    // Checkboxes
    bodyTypeCheckboxes.forEach(cb => {
        cb.addEventListener('change', filterCars);
    });

    // Also listen to the Search button in the top bar (inventory-form) to force filter
    const searchForms = document.querySelectorAll('form');
    searchForms.forEach(form => {
        form.addEventListener('submit', function (e) {
            e.preventDefault(); // Prevent page reload
            filterCars();
        });
    });

    // Trigger initial filter (to clear any previous state if needed)
    filterCars();
});
