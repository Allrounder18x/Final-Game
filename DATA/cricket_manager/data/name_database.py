"""
Comprehensive Name Database for Player Generation
Extracted from gamer 2024.py with regional name lists
"""

# British/Western forenames
BRITISH_FORENAMES = [
    "James", "John", "William", "David", "Michael", "Robert", "Richard", "Thomas", "Christopher", "Daniel",
    "Paul", "Mark", "George", "Steven", "Andrew", "Edward", "Joseph", "Charles", "Stephen", "Matthew",
    "Anthony", "Donald", "Kevin", "Jason", "Jeffrey", "Ryan", "Gary", "Timothy", "Scott", "Benjamin",
    "Nicholas", "Jonathan", "Brian", "Adam", "Peter", "Ronald", "Kenneth", "Gregory", "Patrick", "Frank",
    "Alexander", "Raymond", "Jack", "Dennis", "Jerry", "Tyler", "Aaron", "Jose", "Henry", "Douglas",
    "Carl", "Arthur", "Roger", "Joe", "Juan", "Albert", "Justin", "Terry", "Gerald", "Keith",
    "Samuel", "Willie", "Ralph", "Lawrence", "Roy", "Bruce", "Brandon", "Harry", "Fred", "Wayne",
    "Billy", "Steve", "Louis", "Jeremy", "Randy", "Howard", "Eugene", "Carlos", "Russell", "Bobby",
    "Victor", "Martin", "Ernest", "Phillip", "Todd", "Jesse", "Craig", "Alan", "Shawn", "Clarence",
    "Sean", "Philip", "Chris", "Johnny", "Earl", "Jimmy", "Antonio", "Danny", "Bryan", "Tony"
]

# Muslim/Pakistani/Bangladeshi/Afghan forenames
MUSLIM_FORENAMES = [
    "Ahmed", "Mohammed", "Ali", "Hassan", "Hussain", "Omar", "Yusuf", "Ibrahim", "Ismail", "Abdullah",
    "Abdul", "Khalid", "Sami", "Bilal", "Imran", "Zaid", "Zain", "Faisal", "Farhan", "Hamza",
    "Salman", "Suleiman", "Tariq", "Rashid", "Junaid", "Naveed", "Shoaib", "Saad", "Ayaan", "Rayyan",
    "Sameer", "Shahid", "Asad", "Adeel", "Adnan", "Ammar", "Anas", "Arif", "Aziz", "Bashir",
    "Danish", "Dawood", "Ehsan", "Faiz", "Fahad", "Fahim", "Faraz", "Fawad", "Ghafoor", "Habib",
    "Hakeem", "Haroon", "Hasan", "Hashim", "Iftikhar", "Ilyas", "Jabir", "Jamal", "Jawad", "Kashif",
    "Khalil", "Latif", "Luqman", "Mahmood", "Majid", "Mansoor", "Mehmood", "Moin", "Munir", "Mustafa",
    "Nadeem", "Naeem", "Naseem", "Nasir", "Nawaz", "Noman", "Owais", "Parvez", "Qasim", "Qudrat",
    "Rafaqat", "Rafiq", "Rahim", "Rashad", "Rauf", "Rehan", "Saif", "Sajid", "Samiullah", "Sarfaraz",
    "Shabbir", "Shafqat", "Shahbaz", "Shahzad", "Shakil", "Sharif", "Shehzad", "Sohail", "Sultan", "Tabish",
    "Tahir", "Talha", "Tanveer", "Tauqeer", "Usama", "Usman", "Waqas", "Wasim", "Yahya", "Yasir",
    "Younis", "Zafar", "Zahid", "Zakir", "Zeeshan", "Zubair", "Ahsan", "Aqib", "Arsalan", "Asif",
    "Atif", "Ayaz", "Azhar", "Babar", "Basharat", "Basit", "Ejaz", "Fahd", "Faiq", "Farrukh",
    "Fazal", "Feroz", "Ghazanfar", "Ghulam", "Hammad", "Haseeb", "Hussam", "Ibad", "Ibrar", "Idrees",
    "Irfan", "Javed", "Kamran", "Kashan", "Khurram", "Mairaj", "Mansur", "Masood", "Mazhar", "Mubashir",
    "Mujahid", "Munawwar", "Murtaza", "Nabeel", "Nashit", "Obaid", "Qaiser", "Qamar", "Qudratullah", "Rameez",
    "Rayhan", "Rizwan", "Saifullah", "Sajjad", "Sarmad", "Shaheryar", "Shahmir", "Shamsher", "Shariq", "Sibtain",
    "Sikandar", "Sufyan", "Taimoor", "Umair", "Umar", "Waleed", "Waseem", "Yamin"
]

# Indian/Hindu forenames
INDIAN_FORENAMES = [
    "Arjun", "Rahul", "Vikram", "Rohit", "Amit", "Suresh", "Sanjay", "Anil", "Rajesh", "Sunil",
    "Karan", "Manish", "Deepak", "Prakash", "Vivek", "Ajay", "Rakesh", "Abhishek", "Naveen", "Gaurav",
    "Aakash", "Harsh", "Siddharth", "Yash", "Kunal", "Nikhil", "Pankaj", "Rajat", "Sandeep", "Tarun",
    "Varun", "Vishal", "Aman", "Ankit", "Ashish", "Dev", "Jatin", "Kapil", "Mayank", "Neeraj",
    "Parth", "Rishi", "Sahil", "Sameer", "Shivam", "Sumit", "Uday", "Vikas", "Yogesh", "Rohin",
    "Aditya", "Aarav", "Ishaan", "Kabir", "Lakshya", "Mihir", "Naman", "Om", "Pranav", "Rudra",
    "Shaurya", "Tejas", "Utkarsh", "Vihaan", "Zayan", "Bhavesh", "Chirag", "Dhruv", "Eshan", "Faizal",
    "Girish", "Hemant", "Inder", "Jai", "Keshav", "Lalit", "Mukul", "Nilesh", "Onkar", "Praveen",
    "Ravindra", "Saket", "Tanmay", "Umesh", "Vibhor", "Yatin", "Zubin", "Harshit", "Jignesh", "Kartik",
    "Luv", "Madhav", "Nirav", "Ojas", "Pranay", "Samar", "Tushar", "Viren", "Ajeet", "Bharat",
    "Chetan", "Dilip", "Eklavya", "Gopal", "Harshad", "Jaspreet", "Kailash", "Manoj", "Omkar", "Puneet",
    "Qadir", "Ramesh", "Sanjiv", "Tapan", "Vasant", "Yogendra", "Amitabh", "Bhupendra", "Chandan", "Devendra",
    "Eshwar", "Farhan", "Hemendra", "Indrajit", "Jitendra", "Kiran", "Lokesh", "Mahesh", "Nitin", "Ravish",
    "Tej", "Ujjwal", "Vijay", "Yashwant", "Anirudh", "Bhuvan", "Chaitanya", "Dhananjay", "Harinder", "Iqbal",
    "Jagdish", "Kishore", "Mitesh", "Utsav", "Vikrant", "Yuvraj", "Zain", "Ajinkya", "Bhaskar", "Chiranjiv",
    "Dinesh", "Gautam", "Ishan", "Manan"
]

# Sri Lankan forenames
SRI_LANKAN_FORENAMES = [
    "Kumar", "Dinesh", "Upul", "Nuwan", "Chaminda", "Mahela", "Angelo", "Thisara", "Lasith", "Dilshan",
    "Suranga", "Kusal", "Dhananjaya", "Lahiru", "Roshen", "Asela", "Isuru", "Chamara", "Jeewan", "Pradeep",
    "Dimuth", "Avishka", "Pathum", "Charith", "Wanindu", "Dasun", "Minod", "Oshada", "Ramesh", "Vishwa",
    "Sadeera", "Niroshan", "Kasun", "Shehan", "Nipun", "Sandun", "Dilum", "Vikum", "Nuwanidu", "Nishan"
]

# British/Western surnames
BRITISH_SURNAMES = [
    "Smith", "Jones", "Taylor", "Brown", "Williams", "Wilson", "Johnson", "Davies", "Robinson", "Wright",
    "Thompson", "Evans", "Walker", "White", "Roberts", "Green", "Hall", "Wood", "Jackson", "Clarke",
    "Harris", "Clark", "Scott", "Turner", "Hill", "Moore", "Cooper", "Ward", "Morris", "King",
    "Watson", "Harrison", "Morgan", "Baker", "Edwards", "Collins", "Stewart", "Marshall", "Owen", "Elliott",
    "Reynolds", "Saunders", "Fox", "Graham", "Murray", "Hamilton", "Hughes", "Gibson", "Ellis", "Wilkinson",
    "Foster", "Thomson", "Gordon", "Russell", "Pearson", "Holmes", "Mills", "Simpson", "Reid", "Ross",
    "Henderson", "Paterson", "Jenkins", "Booth", "Walsh", "Hunter", "Young", "Gray", "Harding", "Mitchell",
    "Phillips", "Johnston", "Harvey", "Dunn", "Wallace", "Woods", "Black", "Ferguson", "Alexander", "Parsons",
    "Hart", "Lawson", "McDonald", "Fraser", "Grant", "Carr", "Anderson", "Matthews", "Patel", "Richardson",
    "Riley", "Bennett", "Cook", "Bailey", "Bell", "Barker", "Murphy", "Kelly", "Powell", "Begum",
    "Moss", "Sharp", "Day", "Brooks", "Atkinson", "Holland", "Allen", "Dawson", "Chapman", "Lawrence",
    "Fuller", "Griffiths", "Willis", "Marsh", "Cunningham", "Stephenson", "Nicholson", "Burns", "Jennings",
    "Ball", "Burton", "Spencer", "Walters", "Hewitt", "Jordan", "Lloyd", "Knight", "Rowe", "Armstrong",
    "Berry", "Wells", "Williamson", "Bates", "Garner", "Hayward", "Gregory", "Newton", "Reeves", "Potter",
    "Duncan", "Fletcher", "Andrews", "Goodwin", "Higgins", "Watkins", "Francis", "Stevenson", "Oliver", "Holt",
    "Frost", "Bird", "Burgess", "Chambers", "Sutton", "Cooke", "Yates", "Pearce", "Dean", "Shepherd",
    "Lowe", "Barnett", "Fowler", "Greenwood", "Hardy", "Watts", "Barrett", "Freeman", "Hartley", "Buckley",
    "Davidson", "Cross", "Byrne", "Doyle", "Hammond", "Townsend", "Carpenter"
]

# Muslim/Pakistani/Bangladeshi/Afghan surnames
MUSLIM_SURNAMES = [
    "Khan", "Malik", "Sheikh", "Qureshi", "Ansari", "Syed", "Chaudhry", "Farooqi", "Hashmi", "Abbasi",
    "Siddiqui", "Jafri", "Zaidi", "Rizvi", "Naqvi", "Kazmi", "Mirza", "Baig", "Butt", "Dar",
    "Awan", "Rana", "Bhatti", "Cheema", "Gondal", "Gujjar", "Jutt", "Mughal", "Rajput", "Shaikh",
    "Tariq", "Yousafzai", "Afridi", "Alvi", "Azmi", "Barakzai", "Bukhari", "Chishti", "Durrani", "Faruqi",
    "Gilani", "Haider", "Hussain", "Iqbal", "Jahangir", "Janjua", "Kashmiri", "Kiani", "Kiyani", "Lodhi",
    "Mahmood", "Mehmood", "Mir", "Moinuddin", "Mumtaz", "Munir", "Mustafa", "Naseer", "Niazi", "Noor",
    "Paracha", "Pirzada", "Qadri", "Qazi", "Tabani", "Raja", "Mirchiwala", "Rehman", "Sabir", "Sadiq",
    "Saeed", "Safi", "Sajjad", "Saleem", "Salim", "Sami", "Sarwar", "Shah", "Shahid", "Shamsi",
    "Sharif", "Shaukat", "Sherazi", "Siddiqi", "Sohail", "Sultan", "Tabassum", "Tahir", "Talib", "Tanveer",
    "Usmani", "Wahid", "Wali", "Yasin", "Yousaf", "Bottlewala", "Zafar", "Zahid", "Zaman", "Zia",
    "Zubair", "Abidi", "Agha", "Ahsan", "Akhtar", "Alam", "Ali", "Amjad", "Anwar", "Arif",
    "Asghar", "Aslam", "Azhar", "Aziz", "Babar", "Bashir", "Basit", "Chaudhary", "Danish", "Ejaz",
    "Faisal", "Farrukh", "Fazal", "Feroz", "Ghafoor", "Ghani", "Habib", "Hafeez", "Hameed", "Hamid",
    "Hanif", "Hassan", "Iftikhar", "Ilyas", "Imran", "Irfan", "Ismail", "Jamal", "Javed", "Kaleem",
    "Kamran", "Kashif", "Khalid", "Latif", "Majid", "Manzoor", "Masood", "Mazhar", "Moin", "Mujahid",
    "Nadeem", "Naeem", "Naseem", "Nasir", "Nawaz", "Noman", "Obaid", "Parvez", "Qaiser", "Qamar",
    "Qasim", "Rafaqat", "Rafiq", "Rahim", "Khanzada", "Rayyan", "Rehan", "Saad", "Sajid", "Shabbir",
    "Shafqat", "Shahbaz", "Shahzad", "Shakil", "Shehzad", "Shoaib", "Batliwala", "Kabadi", "Talha", "Kabadia",
    "Tauqeer", "Usama", "Usman"
]

# Indian/Hindu surnames
INDIAN_SURNAMES = [
    "Sharma", "Verma", "Singh", "Patel", "Kumar", "Gupta", "Reddy", "Nair", "Mehta", "Jain",
    "Joshi", "Rao", "Das", "Iyer", "Chopra", "Kapoor", "Agarwal", "Choudhary", "Yadav", "Mishra",
    "Pandey", "Tripathi", "Srivastava", "Dubey", "Tiwari", "Shukla", "Bansal", "Saxena", "Sethi", "Malhotra",
    "Bhatia", "Bhatt", "Desai", "Naidu", "Shetty", "Shekhar", "Srinivasan", "Krishnan", "Menon", "Pillai",
    "Rastogi", "Chatterjee", "Mukherjee", "Banerjee", "Ghosh", "Dutta", "Bose", "Sarkar", "Chakraborty", "Roy",
    "Paul", "Sen", "Dasgupta", "Lal", "Aggarwal", "Goel", "Mittal", "Chawla", "Grover", "Sodhi",
    "Ahluwalia", "Gill", "Kaur", "Sandhu", "Sidhu", "Bedi", "Puri", "Suri", "Sahni", "Talwar",
    "Bajaj", "Bhasin", "Bhandari", "Bhat", "Bharadwaj", "Chandra", "Chhabra", "Choudhury", "Dey", "Dixit",
    "Gandhi", "Garg", "Goyal", "Jha", "Jindal", "Khandelwal", "Khatri", "Kohli", "Kulkarni", "Mahajan",
    "Malik", "Mani", "Mathur", "Mitra", "Modi", "Monga", "Moolchandani", "Mundra", "Murthy", "Nanda",
    "Narang", "Nath", "Nayak", "Ojha", "Panda", "Pandit", "Parikh", "Parmar", "Pathak", "Poddar",
    "Prasad", "Purohit", "Raghavan", "Rai", "Raj", "Rana", "Rathi", "Rawat", "Sachdeva", "Sagar",
    "Sahu", "Saini", "Saluja", "Sampath", "Sarin", "Sarraf", "Sehgal", "Shah", "Shetty", "Sibal",
    "Sikdar", "Singhania", "Sinha", "Somani", "Soni", "Sood", "Srinivas", "Suri", "Swamy", "Tandon",
    "Thakur", "Thapar", "Trivedi", "Upadhyay", "Vaidya", "Varma", "Vasudevan", "Venkatesh", "Vij", "Vijay",
    "Vora", "Wadhwa", "Yarlagadda", "Zaveri", "Chauhan", "Solanki", "Bhalla", "Bisht", "Bora", "Dabral",
    "Dangi", "Dewan", "Gairola", "Goswami", "Guleria", "Kandwal", "Kanyal", "Kashyap", "Khanduri", "Kothari",
    "Negi", "Pal", "Pant", "Pathania", "Phukan", "Pokhriyal", "Rawal", "Sati", "Semwal", "Thapliyal",
    "Tolia", "Uniyal", "Biswas", "Chakma"
]

# Sri Lankan surnames
SRI_LANKAN_SURNAMES = [
    "Perera", "Jayawardene", "Sangakkara", "Mendis", "Fernando", "Silva", "Herath", "Mathews", "Karunaratne", "Chandimal",
    "Gunathilaka", "Lakmal", "Thirimanne", "Kusal", "Pradeep", "Jayasinghe", "Weeraratne", "Vaas", "Dilshan", "Senanayake",
    "Kulasekara", "Rathnayake", "Bandara", "Wickramasinghe", "Ratnayake", "De Silva", "Samarawickrama", "Gunaratne", "Pathirana", "Madushanka",
    "Abeywickrama", "Amarasinghe", "Ariyaratne", "Balasuriya", "Basnayake", "Bopage", "Dassanayake", "De Alwis", "De Mel", "De Soysa",
    "Dias", "Dissanayake", "Ekanayake", "Gamage", "Gunasekara", "Gunawardena", "Hapugoda", "Hettiarachchi", "Jayalath", "Jayasekara",
    "Jayatilleke", "Jayasuriya", "Kariyawasam", "Kodikara", "Kularatne", "Kuruppu", "Liyanage", "Madduma", "Munasinghe", "Nandasena",
    "Piyadasa", "Rajapaksa", "Rajapakse", "Ranasinghe", "Ranatunga", "Samarakoon", "Samarasinghe", "Siriwardena", "Sumanasekera", "Thilakaratne",
    "Udawatte", "Vidanapathirana", "Wijeratne", "Wijesekera", "Wijesinghe", "Wimalasena", "Withanage", "Yapa", "Yasaratne", "Yatawara",
    "Yatigammana", "Yatipiyage", "Abeykoon", "Abeysekera", "Arachchi", "Atapattu", "Balachandra", "Bandaranayake", "Boteju", "Chandrasiri",
    "Dahanayake", "De Costa", "De Fonseka", "Dharmasena", "Edirisinghe", "Gajanayake", "Jayakody", "Jayatissa", "Jayasundara"
]


# Regional mapping
REGION_MAP = {
    # South Asian Muslim countries
    'Pakistan': ('muslim', 'muslim'),
    'Bangladesh': ('muslim', 'muslim'),
    'Afghanistan': ('muslim', 'muslim'),
    
    # South Asian Hindu/Buddhist countries
    'India': ('indian', 'indian'),
    'Sri Lanka': ('sri_lankan', 'sri_lankan'),
    'Nepal': ('indian', 'indian'),
    
    # Western/British influenced
    'England': ('british', 'british'),
    'Australia': ('british', 'british'),
    'New Zealand': ('british', 'british'),
    'South Africa': ('british', 'british'),
    'West Indies': ('british', 'british'),
    'Ireland': ('british', 'british'),
    'Scotland': ('british', 'british'),
    'Zimbabwe': ('british', 'british'),
    
    # Middle East
    'UAE': ('muslim', 'muslim'),
    'Oman': ('muslim', 'muslim'),
    'Kuwait': ('muslim', 'muslim'),
    'Bahrain': ('muslim', 'muslim'),
    'Qatar': ('muslim', 'muslim'),
    'Saudi Arabia': ('muslim', 'muslim'),
    
    # Default for others
    'default': ('british', 'british')
}


def get_name_lists(team_name):
    """Get appropriate name lists for a team"""
    # Get region mapping
    first_region, last_region = REGION_MAP.get(team_name, REGION_MAP['default'])
    
    # Map regions to name lists
    first_names_map = {
        'british': BRITISH_FORENAMES,
        'muslim': MUSLIM_FORENAMES,
        'indian': INDIAN_FORENAMES,
        'sri_lankan': SRI_LANKAN_FORENAMES
    }
    
    last_names_map = {
        'british': BRITISH_SURNAMES,
        'muslim': MUSLIM_SURNAMES,
        'indian': INDIAN_SURNAMES,
        'sri_lankan': SRI_LANKAN_SURNAMES
    }
    
    first_names = first_names_map.get(first_region, BRITISH_FORENAMES)
    last_names = last_names_map.get(last_region, BRITISH_SURNAMES)
    
    return first_names, last_names
