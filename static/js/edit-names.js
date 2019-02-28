$(function() {
  $('.name-field').on('keypress', function(evt) {
    const $this = $(this);
    // When the enter key was pressed
    if (evt.which == 13) {
      const name = $this.val();
      const person_id = parseInt($this.data('personid'));
      const data = {
        'person_id': person_id,
        'name': name
      };

      // AJAX call to update database
      $.post('/edit_name', data, function(response) {
        if (response === 'True') {
          const $nameDiv = $('<div>', {
            'class': 'name-container__name',
            'html': name
          });
          const $nameContainerDiv = $('<div>', {
            'class': 'person__name-container'
          });
          $nameContainerDiv.append($nameDiv);
          $this.replaceWith($nameContainerDiv);
        }
      });
    }
  });
});
