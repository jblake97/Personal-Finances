# Personal Finances
#### Video Demo: https://www.youtube.com/watch?v=3Mi4zCkyME0

<br>

#### APP OVERVIEW
This app was made from my own inspiration to create a web app to help manage someones finances on a monthly basis.
I personally have used a google spreadsheet to do such thing for a few years. Moving forward, my intent when
designing this app was to develop it to a point where I could migrate to using the app! Therefore, I put in extensive
effort to add intuitive features that would not make the app feel clunky and a pain to use. As you will discover in this
read me file, this app contains several features, all of which are user-proof, that allow for seamless use of the app.

<br>

#### APP ARCHITECTURE
This app was built with a HTML, CSS, Javascript, and JJANGO front-end. This allowed me to create web user interfaces
that are simple to program and operate. HTML is HTML, nothing fancy. CSS helped make the web application look presentable.
(I also used external CSS libraries such as Bootstrap.) Javascript came into handy when wanting to make each page more
interactive for the user. Javascript was used in several areas throughout the application. JJANGO allowed for the front
end of the app to communicate with the back-end. That back-end was Python with the Flask API. Python and flask were the
obvious choice for the back-end logic as 1) that is what we learned in CS50, and 2) python and flask are simple to
understand and implement, but still have enough features to make a full web app. The final piece to the architecture is
the database. As this web application is meant to be used by a logged in user, it was essential to be able to store each
users' data to a database. SQLite was the obvious choice here. Very simple to use, takes up minimal resources, and it
again is what we learned in CS50.

<br>

#### USER REGISTRATION AND LOGGING IN
The first feature to implement was the ability for a user to register and a user to log in to an already created account.
The design thought here is to have a databse that has a table of 'users'. Each user would require a username, password, an email, and be automatically assigned a 'userID'. The front end only asks for a username, password, and an email while the back-end then automatically inserts the new user into the users table, checking for duplicates, and then automatically assigning a 'userID'. The password is already ran through a hash so no plain text passwords are stored in the database, only the hash of the passwords.
<br>
The log in function works quite similar. It prompts the user to enter a username and a password. The back end then queries the database to find a match, (while hashing and checking the hash of the plain text password), and if it is successful it logs the user in.

#### HOMEPAGE/INDEX
The homepage of the web app is the 'summary' page. Here, a HTML table displays the users monthly income, monthly bills, monthly spending, and their remaining balance. This table automatically updates each time a new item is added to any of the above categories. There is no functionality here besides just always displaying the most updated financial information.
<br>

#### ADDING SPENDING
In order to track one's monthly finances, they need to track each purchase they make. Some purchases are fixed every month, like rent and bills, and we'll get into those later. However, buying a cup of coffee on a random Wednesday morning is a bit less predictable, more sparatic. Therefore, I created a category called 'spending'. Here, the user is able to add any random spending they do throughout the month. A text field takes the dollar amount, a drop-down menu provides users with different payment methods to select, all of which the user can edit, and thne a text field to take a item description. Beneath the inputs, there is a submit and remove button. Upon clicking submit, the new entry is inserted into the SQL table on the back-end and the updated 'spending' table is displayed. Now, within the 'spending' table, a column called 'Delte?' exists. This allows the user to check any row, and then click the remove button. This removes any entries from the table in case the user made a mistake when inputting their expense. The front-end implements javascript to inhibit the user from inputting certain text into certain fields. Example, user can only input numbers and decimals into the $ amount field. This was done as a pre-caution to user error. Javascript also allows for the interactivity of the submit & remove button turning 'on' when certain fields have information in them. Javascript also allows for the removing functionality without having a completely separate HTML page to do so.
<br>

#### ADDING INCOME
Similar to the spending functionality, adding income behaves in almost the same manner. This route, or HTML page, allows the user to input income into an income SQL table on the back-end that is tied to the specific user. The income page asks for a $ amount and a description and then allows the user to click submit. Upon clicking submit, the income is added to the user's account and the income table is updated along with the total at the bottom of the screen. On the back-end, this income is added to the SQL database. The same remove functionality in add spending is also present here.
<br>

#### ADDING BILLS
The other part of monthly spending is the fixed monthly costs. For example, rent, car payment, car insurance, utility bills, phone bill, gym, etc. This HTML page allows the user to enter any bill they'd like that has a $ amount and description. Once the inputs are filled, the user can click submit and then the new bill is added to the SQL table on the back-end and the front-end table is updated. Again, the same remove functionality is present here as well.
<br>

#### PAYMENT METHODS
Along with knowing how much money one person spends and makes, they also may want to know on what payment method did they spend such money. This HTML page allows the user to input a list, from 1 to as many as they'd like, payment methods. These are then tied to the user, (in a SQL table on the back-end), that are then available to the user in their 'add spending' functionality. This gives the flexibility for users to have different payment methods they use. For example, some people use paypal while some prefer venmo. And I am sure some use both. Similar to the other pages, the remove functionality is also present.
<br>

#### CLEARING AND EXPORTING DATA
The last bit of functionality currently implemented in the program is the ability to 'reset' all of the data based on spending, bills, income, and payment methods. This allows the user at the end of the month to cleanly and efficiently wipe all the data they need to. Personally, I would imagine most people would claer the 'spending' table while keeping their 'income' and 'payment methods'. This is implemented through some checkboxes in a HTML form, then having a button called 'reset' that when clicked runs a few SQL execute statements that perform the deleting on the back-end. <br>
Secondly, this HTML page has a second functionality and that is to export and email the data contained in each SQL table to the user's email address. On the front-end, all a user needs to do is click an 'export' button. This triggers the logic on the back-end that then queries for all the user's data, creates excel files of each of the tables, and then packages them all into one email that is then sent to the user's email account.
<br>

#### STYLE
The last element of the project I did not talk about at all is the style, or look, of this project. I wanted a clean, uniform look throughout the entire app. Therefore, I used various CSS selectors and style attributes to keep a uniform look throughout the program. I even was able to learn how to create more visually appealing HTML Tables. Along with the standard CSS, I also referenced an external CSS library called Bootstrap. Bootstrap helped me created clearner looking buttons, inputs, and an overall more professional looking web-app. It also is responsible for the clean and intuitive navigation bar found at the top of the app.

##### TO DO
As one might have concluded, there is a lot of opportunity for expansion upon this app. Firstly, adding the ability to edit entries in the SQL tables rather than delete and re-add. Another functionality would be a way to search the database for a certain 'spending' item the user wants to see. Thirdly, it would be nice if there was functionality to sort the 'spending' table by the table headers rather than just have them displayed chronologically. <br>
I deliberately chose to keep the functionality minimal and straight forward. I thought that it would be great to have all these features, but, i might be biting off more than I could chew and I did not want to over-promsie and under-deliver. Therefore, I do plan on revisiting this app in the future once I have more knowledge and experience under my belt.
