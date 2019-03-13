$(function() {
  $.get('/collections', function(response) {
    response.forEach(function(collection, index) {
      const $collectionInfoContainer = $('.collection-detail').find('[data-collection-id="' + collection.id + '"]');
      const $photoNumEl = $collectionInfoContainer.find('.on-hover-layer__photos-num');
      const $personNumEl = $collectionInfoContainer.find('.on-hover-layer__persons-num');
      $photoNumEl.html(collection.numPhotos + ' photo(s)');
      $personNumEl.html(collection.numPersons + ' person(s)');
    });
  });
});
