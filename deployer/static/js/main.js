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
        credentials: 'same-origin',
        body: JSON.stringify(body)
    });
}

function postAndShowResult(url, content) {
    return fetchAuth(url, content)
        .then(function(response) {
            return response.json();
        })
        .then(function(json) {
            if (!json.success && json.error) {
                alert(json.error);
            } else {
                resultJson = json;
                $('#result-modal').modal('show');
            }
        });
}

$(document).ready(function() {

    $('#versions-table').on('check.bs.table', function ($element, row) {
        selectedImages[row.digest] = row.tag;
    });

    $('#versions-table').on('uncheck.bs.table', function ($element, row) {
        delete selectedImages[row.digest]
    });

    $('#versions-table').on('check-all.bs.table', function ($element, rows) {
        for (var i in rows) {
            selectedImages[rows[i].digest] = rows[i].tag;
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

    $('#versions-table, #deployer-table').on('uncheck-all.bs.table', function ($element, rows) {
        selectedImages = {};
    });

    $('#versions-table, #deployer-table').on('load-success.bs.table', function(data) {
       selectedImages = {};
    });

    $('#result-modal').on('shown.bs.modal', function (e) {
        var modalBody = $('#result-modal .modal-body');
        modalBody.html('');

        for (var i in resultJson) {
            title = resultJson[i]['title'];

            if(!resultJson[i]['success']){
                title += 'Error: ' + title;
            }

            modalBody.append($('<h2>').html(resultJson[i]['title']));
            modalBody.append($('<pre>').html(resultJson[i]['result']));
        }

        resultJson = {};
    });
});
