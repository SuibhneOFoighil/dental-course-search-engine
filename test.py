from utils import extract_reference_numbers

def test_extract_reference_numbers():
    text = "This is a test (1, 2, 3,4,5,6,7,8,9,10,11,12, 13,14,15)"

    print(extract_reference_numbers(text))

    assert extract_reference_numbers(text) == ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15']

    text = """
    Theme 1: Evolution of Orthodontic Techniques and Appliances

    The history of orthodontics is marked by the evolution of techniques and appliances used to straighten teeth. Early methods involved making teeth thinner and attaching a piece of gold or teeth to them (2). The use of a tool called a "pelican" to extract teeth and wire them in place was eventually replaced by using silver wire to push teeth apart and align them (3). The development of different types of bands used in orthodontic treatment, such as silver bands with holes for needles, was also significant (1). The invention of the pin and tube appliance allowed for quick and automatic straightening of teeth (8). The development of stainless steel brackets and the construction of orthodontic arch wires in the 2010s further advanced the field (19, 20). 

    Theme 2: Key Figures and Institutions in Orthodontics

    Several key figures and institutions have shaped the field of orthodontics. Dr. Edward Hartley Angle played a significant role in promoting his appliances and believed that the first upper molar was the key to occlusion (11, 12). Dr. Lysle Johnston was a pioneer in orthodontics and was very concerned about the comfort of his patients (14). He also played a significant role in shaping the field and the University of Michigan's orthodontics program (15, 16). The establishment of the international school for orthodontics from 1915 to the Second World War was a significant milestone (1). The formation of the American Society of Orthodontists and the reorganization of the American Association in 1937 were also important events in the history of orthodontics in the United States (26, 27).

    Theme 3: The Impact of Societal Events and Trends on Orthodontics

    Societal events and trends have had a significant impact on the field of orthodontics. The American Society of Dental Surgeons ceased to exist around 1855 or 1860 due to the Civil War, which was a setback for the field (9). The importance of aesthetics in orthodontics has been increasingly recognized, with a trend towards cosmetology in the field (10). World War II also had an impact on the field, causing divisions in the dental community (28). The financial success of the University of Michigan's orthodontics program and its impact on students is an example of the influence of economic factors on the field (15). The debate between extraction and non-extraction methods in orthodontics, influenced by regional societies, was seen as a moral and religious argument (18)."""

    sorted_references = ['1','2','3','8', '9', '10', '11','12','14','15','16','18','19','20','26','27','28']
    result = extract_reference_numbers(text)
    # remove duplicates
    result = list(set(result))
    # sort
    result.sort(key=lambda x: int(x))
    
    print(result)
    assert result == sorted_references

    text = "This  is a test (1)(2)"

    print(extract_reference_numbers(text))

    assert extract_reference_numbers(text) == ['1','2']

    print("All tests passed!")

def main():
    test_extract_reference_numbers()

if __name__ == "__main__":
    main()