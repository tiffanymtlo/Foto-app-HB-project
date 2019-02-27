$(function() {
  $('.persons__link-btn').on('click', function() {
    let persons_link = '/persons?';
    const $checkedCheckboxes = $('input[name="person_ids[]"]').filter(':checked').map(function() {
      return this.value;
    });

    for (let i = 0; i < $checkedCheckboxes.length; i += 1) {
      persons_link = persons_link + 'person_ids[]=' + $checkedCheckboxes[i] + '&';
    }

    $('.persons__link').attr('href', persons_link);
  });
});
