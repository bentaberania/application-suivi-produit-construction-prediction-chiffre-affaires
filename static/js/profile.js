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


// profile.js

function showForm(personnelId, role) {
	document.getElementById('personnel_id').value = personnelId;
	document.getElementById('editForm').style.display = 'block';
	if (personnelId !== 'new') {
					var selectedPersonnel = document.querySelector('tr[data-id="' + personnelId + '"]');
					var nom = selectedPersonnel.querySelector('td:nth-child(1)').innerText;
					var prenom = selectedPersonnel.querySelector('td:nth-child(2)').innerText;
					var email = selectedPersonnel.querySelector('td:nth-child(3)').innerText;
					var telephone = selectedPersonnel.querySelector('td:nth-child(4)').innerText;
					document.getElementById('nom').value = nom;
					document.getElementById('prenom').value = prenom;
					document.getElementById('email').value = email;
					document.getElementById('telephone').value = telephone;
	} else {
					document.getElementById('nom').value = '';
					document.getElementById('prenom').value = '';
					document.getElementById('email').value = '';
					document.getElementById('telephone').value = '';
					document.getElementById('mot_passe').value = '';
	}
}

function hideForm() {
	document.getElementById('editForm').style.display = 'none';
}

function deletePersonnel(personnelId, role) {
	if (confirm('Êtes-vous sûr de vouloir supprimer ce personnel ?')) {
					fetch('/delete_personnel', {
									method: 'POST',
									headers: {
													'Content-Type': 'application/json',
									},
									body: JSON.stringify({ personnel_id: personnelId, role: role })
					}).then(response => {
									if (response.ok) {
													document.querySelector('tr[data-id="' + personnelId + '"]').remove();
									} else {
													alert('Erreur lors de la suppression du personnel.');
									}
					});
	}
}

function confirmLogout(event) {
	event.preventDefault();  // Empêcher le comportement par défaut du lien
	var result = confirm("Êtes-vous sûr de vouloir vous déconnecter ?");
	if (result) {
					window.location.href = logoutConfirmUrl; // Utiliser l'URL définie dans qrbar.html
	}
}