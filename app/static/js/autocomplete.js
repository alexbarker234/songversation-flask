/* autocomplete.js */

$(window).on("load", function () {
    $(document).on("click", ".autocomplete-options li", function (e) {
        selectAutocomplete($(e.target).parent().parent(), e.target.innerHTML);
    });

    // close autocomplete menu
    $(document).on("click", ".autocomplete-options", function (e) {
        e.stopPropagation(); // dont close when clicking this
    });
    $(document).on("click", function (e) {
        // remove display if it wasnt the element clicked
        $(".autocomplete-input").each(function (index) {
            setAutocompleteVisibility($(this).parent(), e.target == this);
        });
    });

    // manage keyboard
    $(document).on("keyup", ".autocomplete-input", onAutocompleteKeyPress);

    $(document).on("keydown", autocompleteKeyControls);
});

/**
 * Set the visibility of the selected autocomplete options
 * @param {*} autocomplete - the .autocomplete-wrapper element to set option visibility to
 * @param {*} enabled - whether the options should be enabled
 */
function setAutocompleteVisibility(autocomplete, enabled) {
    autocomplete = $(autocomplete);
    autocomplete.children(".autocomplete-options:first-child").css("display", enabled ? "" : "none");
}

/**
 * Sets the input of the autocomplete to a value
 * @param {*} autocomplete - the .autocomplete-wrapper element to set option visibility to
 * @param {*} value - the value to set the autocomplete input to
 */

function selectAutocomplete(autocomplete, value) {
    autocomplete = $(autocomplete);
    console.log(autocomplete)
    autocomplete.children(".autocomplete-input").first().val(value);
    setAutocompleteVisibility(autocomplete, false);
}

function onAutocompleteKeyPress(e) {
    if (e.keyCode == keyUp || e.keyCode == keyDown || e.keyCode == keyEnter) return;

    setAutocompleteVisibility(e.target, true);
    filterOptions($(e.target).parent());
}

/**
 * Changes which elements are displayed from the .autocomplete-options list
 * @param {*} autocomplete - the .autocomplete-wrapper element to set option visibility to
 */
function filterOptions(autocomplete) {
    autocomplete = $(autocomplete);
    let input = autocomplete.children(".autocomplete-input").first();
    let optionList = autocomplete.children(".autocomplete-options").first();
    let options = optionList.find("li");

    optionCount = 0;

    let filter = input.val().toUpperCase();

    for (i = 0; i < options.length; i++) {
        txtValue = options[i].textContent || options[i].innerText;
        // if the input isnt blank and the value matches then display
        if (input.val() != "" && txtValue.toUpperCase().indexOf(filter) > -1) {
            $(options[i]).css("display", "");
            optionCount++;
        } else {
            $(options[i]).css("display", "none");
        }
        $(options[i]).removeClass("selected");
    }
}

/**
 *
 * @param {*} e
 * @returns
 */
function autocompleteKeyControls(e) {
    if ((e.keyCode != keyUp && e.keyCode != keyDown && e.keyCode != keyEnter) || optionCount == 0) return;
    e.preventDefault();

    let autocomplete = e.target;

    let optionsList = autocomplete.children(".autocomplete-options:first-child");
    let options = optionsList.find("li");
    let enabled = options.toArray().filter((elem) => elem.style.display != "none");
    let optionHeight = options.first().height() * 2;

    console.log(autocomplete);

    if (e.keyCode == keyUp || e.keyCode == keyDown) {
        if (optionsList.css("display") == "none") return;

        if (e.keyCode == keyUp) {
            if (autocompleteSelected == -1) autocompleteSelected++;
            autocompleteSelected = (autocompleteSelected - 1).mod(optionCount);
        } else if (e.keyCode == keyDown) {
            autocompleteSelected = (autocompleteSelected + 1).mod(optionCount);
        }

        optionsList.scrollTop(autocompleteSelected * optionHeight);

        // highlight selected
        for (i = 0; i < enabled.length; i++) {
            if (i == autocompleteSelected) $(enabled[i]).addClass("selected");
            else $(enabled[i]).removeClass("selected");
        }
    } else if (e.keyCode == keyEnter) {
        // submit
        if (optionsList.css("display") == "none") checkButton();
        // choose
        else if (autocompleteSelected != -1) selectAutocomplete(enabled[autocompleteSelected].innerHTML);
    }
}
