"""Small word lists used as supporting evidence (never as the only trigger).

All names are common given/family names, lower-case and accent-free. The lists are
deliberately short and can be extended without touching any logic."""

FIRST_NAMES = frozenset("""
aarav aditya amit anil anita anjali ankit arjun arun asha deepak deepika divya ganesh gaurav geeta
gopal hari harish isha jaya kavita kiran krishna kunal lakshmi manoj meena mohit mukesh nandini
neha nikhil nisha pooja prakash pratik priya rahul rajesh rakesh ramesh ravi rekha rohan rohit
sandeep sanjay sanjana sapna seema shreya shyam sneha sunil suresh swati tanvi uday varun vijay
vikas vikram vinod yash zoya meera kabir sneha arjun aisha fatima ahmed mohammed wei olivia noah
liam sophia lucas mia ethan isabella henry grace jack lily john mary james patricia robert
jennifer michael linda william elizabeth david susan richard jessica joseph sarah thomas karen
charles nancy daniel emma chloe fiona hannah elena leila nadia anna maria jose juan carlos
""".split())

LAST_NAMES = frozenset("""
sharma verma gupta singh kumar patel reddy nair iyer mehta joshi desai shah agarwal mishra yadav
chauhan pandey tiwari bose das ghosh banerjee chatterjee rao naidu pillai menon kapoor malhotra
khanna bhatia sinha jain thakur rathore khan ansari qureshi sheikh siddiqui kulkarni bhatt
smith johnson williams brown jones garcia miller davis wilson anderson taylor moore martin lee
walker hall young king wright
""".split())

# Words that make a capitalised phrase an organisation, place or product rather than a person.
ORG_WORDS = frozenset("""
pvt ltd llp llc inc corp corporation company co limited private foods logistics industries
traders enterprises solutions systems technologies services supplies group holdings bank
university college school hospital clinic hotel restaurant store shop mart market agency
associates partners consulting labs institute foundation trust society club
""".split())
