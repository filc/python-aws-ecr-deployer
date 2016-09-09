var selectedImages = {};
var resultJson = {};

function fetchAuth(url, body) {
    var headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
    }

    if (basicAuth) {
        headers['Authorization'] = "Basic " + basicAuth;
    }

    return fetch(baseUrl + url, {
        method: 'post',
        headers: headers,
        body: JSON.stringify(body)
    });
}

function deployImages(images, deployButton) {
    return fetchAuth('/deploy', images)
        .then(function(response) {
            return response.json();
        })
        .then(function(json) {
            resultJson = json;
            $('#result-modal').modal('show');
        });
}

$(document).ready(function() {

    $('#version-table').on('check.bs.table', function ($element, row) {
        console.log(row);
        selectedImages[row.digest] = row.version;
    });

    $('#version-table').on('uncheck.bs.table', function ($element, row) {
        delete selectedImages[row.digest]
    });

    $('#version-table').on('check-all.bs.table', function ($element, rows) {
        for (var i in rows) {
            selectedImages[rows[i].digest] = rows[i].version;
        }
    });

    $('#deployer-table').on('check.bs.table', function ($element, row) {
        selectedImages[row.image_name] = row.ecr_version;
    });

    $('#deployer-table').on('uncheck.bs.table', function ($element, row) {
        delete selectedImages[row.image_name]
    });

    $('#deployer-table').on('check-all.bs.table', function ($element, rows) {
        for (var i in rows) {
            selectedImages[rows[i].image_name] = rows[i].ecr_version;
        }
    });

    $('#version-table, #deployer-table').on('uncheck-all.bs.table', function ($element, rows) {
        selectedImages = {};
    });

    $('#version-table, #deployer-table').on('load-success.bs.table', function(data) {
       selectedImages = {};
    });

    $('#result-modal').on('shown.bs.modal', function (e) {
        var modalBody = $('#result-modal .modal-body');

        for (var i in resultJson) {
            title = resultJson[i]['service'];

            if(!resultJson[i]['success']){
                title += 'Error: ' + title;
            }

            modalBody.append($('<h2>').html(resultJson[i]['service']));
            modalBody.append($('<pre>').html(resultJson[i]['result']));
        }

        resultJson = {};
    });
});
