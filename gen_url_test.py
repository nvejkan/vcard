from urllib.parse import urlencode, quote

def generate_url(
    fn, ln,
    tfn=None, tln=None, nn=None,
    org=None, bu=None, title=None,
    email=None, tel=None, mobile=None, tel2=None,
    company=None, floor=None, street=None,
    district=None, city=None, postal=None, country=None
):
    base_url = "https://nvejkan.github.io/vcard/"
    
    params = {
        'fn': fn, 'ln': ln, 'tfn': tfn, 'tln': tln, 'nn': nn,
        'org': org, 'bu': bu, 'title': title,
        'email': email, 'tel': tel, 'mobile': mobile, 'tel2': tel2,
        'company': company, 'floor': floor, 'street': street,
        'district': district, 'city': city, 'postal': postal, 'country': country
    }
    
    # Remove None values
    params = {k: v for k, v in params.items() if v}
    
    return f"{base_url}?{urlencode(params, quote_via=quote)}"


# Example
url = generate_url(
    fn="Nattawut",
    ln="Vejkanchana",
    tfn="ณัฐวุฒิ",
    tln="เวชกาญจนา",
    nn="",
    org="PwC",
    bu="Assurance",
    title="Senior Manager",
    email="nattawut.v.vejkanchana@pwc.com",
    tel="+6628441000",
    mobile="+66827890444",
    company="PwC Thailand",
    floor="15th Floor",
    street="Bangkok City Tower 179/74-80 South Sathorn Road",
    district="Thungmahamek Sathorn",
    city="Bangkok",
    postal="10120",
    country="Thailand"
)

print(url)