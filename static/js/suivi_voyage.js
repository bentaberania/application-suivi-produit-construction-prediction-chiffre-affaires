const allSideMenu = document.querySelectorAll('#sidebar .side-menu.top li a');

allSideMenu.forEach(item=> {
	const li = item.parentElement;

	item.addEventListener('click', function () {
		allSideMenu.forEach(i=> {
			i.parentElement.classList.remove('active');
		})
		li.classList.add('active');
	})
});


// TOGGLE SIDEBAR
const menuBar = document.querySelector('#content nav .bx.bx-menu');
const sidebar = document.getElementById('sidebar');

menuBar.addEventListener('click', function () {
	sidebar.classList.toggle('hide');
})


const searchButton = document.querySelector('#content nav form .form-input button');
const searchButtonIcon = document.querySelector('#content nav form .form-input button .bx');
const searchForm = document.querySelector('#content nav form');

searchButton.addEventListener('click', function (e) {
	if(window.innerWidth < 576) {
		e.preventDefault();
		searchForm.classList.toggle('show');
		if(searchForm.classList.contains('show')) {
			searchButtonIcon.classList.replace('bx-search', 'bx-x');
		} else {
			searchButtonIcon.classList.replace('bx-x', 'bx-search');
		}
	}
})





if(window.innerWidth < 768) {
	sidebar.classList.add('hide');
} else if(window.innerWidth > 576) {
	searchButtonIcon.classList.replace('bx-x', 'bx-search');
	searchForm.classList.remove('show');
}


window.addEventListener('resize', function () {
	if(this.innerWidth > 576) {
		searchButtonIcon.classList.replace('bx-x', 'bx-search');
		searchForm.classList.remove('show');
	}
})



const switchMode = document.getElementById('switch-mode');

switchMode.addEventListener('change', function () {
	if(this.checked) {
		document.body.classList.add('dark');
	} else {
		document.body.classList.remove('dark');
	}
})
//suivi

function filterAudit() {
    var form = document.getElementById('filterForm');
    var formData = new FormData(form);

    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                var auditTable = document.getElementById('auditData').getElementsByTagName('tbody')[0];
                auditTable.innerHTML = xhr.responseText;

                // Ajouter les flèches à côté de chaque Code_BV
                var codeBVCells = document.querySelectorAll('#auditData td:first-child');
                codeBVCells.forEach(function(cell) {
                    var codeBV = cell.textContent.trim();  // trim() to remove any extra whitespace
                    var arrowSpan = document.createElement('span');
                    arrowSpan.className = 'arrow';
                    arrowSpan.innerHTML = '→';
                    arrowSpan.onclick = function() {
                        toggleDetails(this, codeBV);
                    };
                    cell.innerHTML = '';
                    cell.appendChild(arrowSpan);
                    cell.appendChild(document.createTextNode(' ' + codeBV));  // add space to separate arrow and codeBV
                });
            } else {
                console.error('Erreur lors de la requête : ' + xhr.status);
            }
        }
    };

    xhr.open('GET', '/filter_audit?' + new URLSearchParams(formData).toString(), true);
    xhr.send();
}

function toggleDetails(element, codeBV) {
    var detailsRow = element.parentNode.parentNode.nextElementSibling;

    if (detailsRow && detailsRow.classList.contains('details-row')) {
        detailsRow.parentNode.removeChild(detailsRow);
    } else {
        var xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 200) {
                    var details = JSON.parse(xhr.responseText);
                    var newRow = document.createElement('tr');
                    newRow.className = 'details-row';
                    var newCell = document.createElement('td');
                    newCell.colSpan = 3;

                    var detailsTable = '<table><thead><tr><th>Code BL</th><th>Nombre d\'entrée</th><th>Nombre de sortie</th><th>Cacheté</th><th>Signe</th></tr></thead><tbody>';
                    details.forEach(function(detail) {
                        var cachete = detail.cachete === 1 ? 'True' : 'False';
                        var signe = detail.signe === 1 ? 'True' : 'False';
                        detailsTable += `<tr><td>${detail.Code_BL}</td><td>${detail.FLG_entre}</td><td>${detail.FLG_sortie}</td><td>${cachete}</td><td>${signe}</td></tr>`;
                    });
                    detailsTable += '</tbody></table>';
                    newCell.innerHTML = detailsTable;
                    newRow.appendChild(newCell);

                    element.parentNode.parentNode.parentNode.insertBefore(newRow, element.parentNode.parentNode.nextElementSibling);
                } else {
                    console.error('Erreur lors de la requête : ' + xhr.status);
                }
            }
        };

        xhr.open('GET', `/get_details/${codeBV}`, true);
        xhr.send();
    }
}
   
  
//logout
function confirmLogout(event) {
	event.preventDefault();  // Empêcher le comportement par défaut du lien
	var result = confirm("Êtes-vous sûr de vouloir vous déconnecter ?");
	if (result) {
		window.location.href = logoutConfirmUrl; // Utiliser l'URL définie dans qrbar.html
	}
}