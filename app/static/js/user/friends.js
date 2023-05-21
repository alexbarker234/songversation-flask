function searchUsers() {
console.log('searching')

    input = $('#user-search-input').first()
    $.getJSON(`/api/search-users?name=${input.val()}`).then((response) => {
        container = $('#user-search-results')
        container.empty()
        response.forEach(user => {
            console.log(user)
            container.append(userResultComponent(user)) 
        });
    });
}