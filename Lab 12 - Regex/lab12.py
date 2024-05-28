import re

def find_email(line, regex):
        matches = re.findall(regex, line)
        return matches


emails = []
regex1 = r'(?<!\S)(?:[a-zA-Z0-9!#$%&\'*+/=?^_`{|}~.-]+|"(?:\\[ -~]|[!#-[^-~])*")@(?:(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}|(?:\[(?:IPv6:)?[a-fA-F0-9:.]+\]))(?!\S)'
regex2= r'(?<!\S)(?:[a-zA-Z0-9!#$%&\'*+/=?^_`{|}~.-]+|"(?:\\[ -~]|[!#-[]|[!#-[^-~])*")@com(?!\S)'
regex3 = r'(?<!\S)(?:[a-zA-Z0-9!#$%&\'*+/=?^_`{|}~.-]+|"(?:\\[ -~]|[!#-[]|[!#-[^-~])*\s+")@(?:(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}|(?:\[(?:IPv6:)?[a-fA-F0-9:.]+\]))(?!\S)'


with open('tekst.txt', 'r') as file:

        for line in file:
        # Check if the line contains an email



                founded_emails = find_email(line, regex1)

                for email in founded_emails:
                        if email not in emails:
                                emails.append(email)

                founded_emails = find_email(line, regex2)

                for email in founded_emails:
                        if email not in emails:
                                emails.append(email)

                                founded_emails = find_email(line, regex2)

                founded_emails = find_email(line, regex3)

                for email in founded_emails:
                        if email not in emails:
                                emails.append(email)
        


for email in emails:
        print(email) 


               




# Zwalidowane adresy:
# • soldat@eu.org
# • mauris@wp.pl                                MAM
# • ”erat nulla”@example.com            
# • Fusce+felis.enim.viverra@com                MAM
# • Suspendisse+eu.est@rop.eu                   MAM
# • \tincidunt”@com.dot                         MAM
# • ” ”@null.nul                                MAM
# • ”erat@nec”@gmail.com                        MAM
# • luctus@[IPv6:2001:db8::ff00:42:8329]        MAM

# Z kolei do złych adresów należą:
# • sem.lectus@org (zakładamy, że do domeny globalnej o najwyższym rzędzie należy tylko
# ‘com’)
# • hac@eta (maile z domen lokalnych zostaną zablokowane na poziomie globalnym)
# • ac@rutrum@non.qorTrue
# • nunc”in dui@.org.pl
# • Sed.tincidunt”,”dolor@tada.tede
# • non@volutpat