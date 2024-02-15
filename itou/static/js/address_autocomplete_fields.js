htmx.onLoad(function () {
  let autocompleteNbErrors = 0;
  let addressSearchInput = $("#id_address_for_autocomplete");
  let addressLine1Input = $("#id_address_line_1");
  let addressLine2Input = $("#id_address_line_2");
  let postCodeInput = $("#id_post_code");
  let cityInput = $("#id_city");
  let inseeCodeHiddenInput = $("#id_insee_code");
  let longitudeHiddenInput = $("#id_longitude");
  let latitudeHiddenInput = $("#id_latitude");
  let geocodingScoreHiddenInput = $("#id_geocoding_score");
  let banApiResolvedAddressInput = $("#id_ban_api_resolved_address");

  // Hide fallback fields.
  let fallbackFields = [addressLine1Input, postCodeInput, cityInput];
  fallbackFields.forEach((element) => {
    $(element).parent(".form-group").addClass("d-none");
  });

  addressSearchInput.on("select2:select", function (e) {
    addressLine1Input.val(e.params.data.name);
    postCodeInput.val(e.params.data.postcode);
    cityInput.val(e.params.data.city);
    inseeCodeHiddenInput.val(e.params.data.citycode);
    longitudeHiddenInput.val(e.params.data.longitude);
    latitudeHiddenInput.val(e.params.data.latitude);
    geocodingScoreHiddenInput.val(e.params.data.score);
    banApiResolvedAddressInput.val(e.params.data.label);
  });
  addressSearchInput.select2({
    ajax: {
      processResults: function (data) {
        // Reset debounce counter
        autocompleteNbErrors = 0;
        var results = data.features.map(function (item, index) {
          var prop = item.properties;
          return {
            id: prop.id,
            text: prop.label,
            city: prop.city,
            name: prop.name,
            postcode: prop.postcode,
            citycode: prop.citycode,
            street: prop.street,
            longitude: item.geometry.coordinates[0],
            latitude: item.geometry.coordinates[1],
            score: prop.score,
            label: prop.label,
          };
        });
        return {
          results,
        };
      },
      error: (jqXHR, textStatus, errorThrown) => {
        autocompleteNbErrors++;

        // Debounce errors. Display the error fallback only when we detect 4 errors in a row
        // For some reasons, the BAN API car return temporary errors
        if (autocompleteNbErrors < 5) {
          return;
        }

        // Delete any initial data that may be present if the job seeker already had an address.
        let fieldstoBeCleaned = [
          addressLine1Input,
          addressLine2Input,
          postCodeInput,
          inseeCodeHiddenInput,
          longitudeHiddenInput,
          latitudeHiddenInput,
        ];
        fieldstoBeCleaned.forEach((element) => {
          element.val("");
        });

        let error_message =
          "Une erreur s'est produite lors de la recherche de l'adresse. Merci de la renseigner dans les champs ci-dessous.";
        let html = `<div class='alert alert-primary' role='alert'>${error_message}</div>`;
        $(addressSearchInput).prop("disabled", true);
        $(addressSearchInput).after(html);
        fallbackFields.forEach((element) => {
          $(element).parent(".form-group").removeClass("d-none");
          $(element).parent(".form-group").addClass("form-group-required");
          $(element).prop("required", true);
        });
      },
    },
  });
});
