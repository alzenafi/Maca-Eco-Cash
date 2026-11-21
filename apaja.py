m = float(input("Masukkan massa benda (kg) : "))
a = float(input("Masukkan luas permukaan (m^2) : "))

tekanan = (m * 10) / a

if tekanan > 5000:
    print("Lantai jebol")
else:
    print("Lantai aman")