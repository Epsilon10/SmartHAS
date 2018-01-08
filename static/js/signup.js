
function emailValidate() {
	let email_field = document.forms["SignupForm"]["Email"].value;
	let re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
	if (re.test(email_field.toLowerCase()))
	{
		return true;
	}

	return false;
	
}

function passwordValidate() 
{
	let password_field = document.forms["SignupForm"]["password"].value;
	let confirm_password = document.forms["SignupForm"]["confirmPassword"].value;

	if (password_field === confirm_password && password_field.length > 6)
	{
		return true;
	}

	return false;
}

function SignUpValidate()
{
	console.log('hiboiiiiiiiimehere')
	let email_help = document.getElementById("email-help");
	let password_help = document.getElementById("password-help")
	if (emailValidate() != true)
	{
		
		document.getElementById("exampleInputEmail1").style.borderColor = "red";
		email_help.text = "";
		email_help.style.color = "red";
		email_help.text = "The email you entered was invalid";
		return false;
	}

	else if (passwordValidate() != true)
	{
		document.getElementById("exampleInputPassword1").style.borderColor = "red";
		password_help.text="";
		password_help.style.color = "red";
		password_help.text = "The password you entered was invalid. It must be at least 6 characters long!!!";
		return false;


	}

	return true;

}





