$(function() {
  $('.persons__content__tab-wrapper .tab-anchor').on('click', function() {
    const $personsContentWrapper = $('.persons__content__wrapper');
    const listStyle = $personsContentWrapper.data('list-style');
    const chosenStyle = $(this).data('style');
    if (chosenStyle !== listStyle) {
      if(chosenStyle === 'grid') {
        // add class style-grid
        $personsContentWrapper.addClass('style-grid');
        // change data attr to grid
        $personsContentWrapper.data('list-style', 'grid');
      }
      else {
        $personsContentWrapper.removeClass('style-grid');
        $personsContentWrapper.data('list-style', 'list');
      }
    }
    
    $(this).parents('.persons__content__tab-wrapper')
      .find('.tab-item .tab-anchor').removeClass('active');

    $(this).addClass('active');
    return false;
  });
});
