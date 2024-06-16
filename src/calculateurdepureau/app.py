import toga
from toga.style import Pack
from toga.style.pack import COLUMN, CENTER
import asyncio


def trouver_cotes_possibles(longueur_m, cote_mini_cm, cote_maxi_cm, precision=2):
    longueur_cm = longueur_m * 100
    cotes_possibles = []
    n = 1
    while True:
        division = longueur_cm / n
        if cote_mini_cm <= division <= cote_maxi_cm:
            cotes_possibles.append((round(division, precision), n))
        elif division < cote_mini_cm:
            break
        n += 1
    return cotes_possibles


def calculer_paquets_de_tuiles(largeur_toiture_cm, largeur_tuile_cm, tuiles_par_paquet, largeur_min_paquet_cm, largeur_max_paquet_cm):
    if largeur_toiture_cm <= 0 or largeur_tuile_cm <= 0 or tuiles_par_paquet <= 0:
        return ["Les valeurs de largeur et de tuiles par paquet doivent être positives."]

    n = largeur_toiture_cm / largeur_tuile_cm
    arrondi_tuiles = n - n % tuiles_par_paquet
    tuiles_trop = round(n) - arrondi_tuiles
    largeur_mod = tuiles_trop * largeur_tuile_cm
    nouv_largeur = largeur_toiture_cm - largeur_mod
    division = arrondi_tuiles / tuiles_par_paquet

    if division == 0:
        return ["La largeur de la toiture est trop petite pour être divisée en paquets."]

    pureau = nouv_largeur / division
    results = []

    if largeur_min_paquet_cm < pureau < largeur_max_paquet_cm:
        results.append(f"Pureau latéral: {pureau:.2f} cm")
        results.append(f"Nombre de divisions: {round(division)}")
    else:
        demi = largeur_tuile_cm / 2
        largeur_demi = nouv_largeur - demi
        pureau2 = largeur_demi / division
        if largeur_min_paquet_cm < pureau2 < largeur_max_paquet_cm:
            results.append(f"Pureau latéral avec demi tuile: {pureau2:.2f} cm")
            results.append(f"Nombre de divisions: {round(division)}")
        else:
            results.append("Aucune solution trouvée.")
    return results


class Calculateurdepureau(toga.App):
    def startup(self):
        self.main_window = toga.MainWindow(title=self.formal_name)
        main_box = toga.Box(style=Pack(alignment=CENTER, direction=COLUMN))

        self.add_image(main_box, "resources/b13.png", 20)
        self.add_label(main_box, "Calcul de Pureau:", 16)

        self.longueur_input = self.add_input(
            main_box, "Longueur entre le premier liteau et le dernier (m):", 10)
        self.cote_mini_input = self.add_input(
            main_box, "Pureau mini de la tuile (cm):")
        self.cote_maxi_input = self.add_input(
            main_box, "Pureau maxi de la tuile (cm):")

        self.calculate_button = toga.Button(
            'Calculer', on_press=self.calculer_cotes, style=Pack(width=100, padding_top=5))
        main_box.add(self.calculate_button)

        self.result_box = toga.Box(style=Pack(
            direction=COLUMN, alignment=CENTER))
        main_box.add(self.result_box)

        self.add_image(main_box, "resources/6.png", 50)
        self.add_label(main_box, "Calcul paquets de tuiles:", 16)

        self.largeur_toiture_input = self.add_input(
            main_box, "Largeur de la toiture (m):", 10)
        self.largeur_tuile_input = self.add_input(
            main_box, "Largeur de la tuile (cm):")
        self.tuiles_par_paquet_input = self.add_input(
            main_box, "Tuiles par paquet:")
        self.largeur_min_paquet_input = self.add_input(
            main_box, "Largeur min paquet (cm):")
        self.largeur_max_paquet_input = self.add_input(
            main_box, "Largeur max paquet (cm):")

        self.calculate_button_2 = toga.Button(
            'Calculer', on_press=self.calculer_paquets, style=Pack(width=100, padding_top=5))
        main_box.add(self.calculate_button_2)

        self.result_box_2 = toga.Box(style=Pack(
            direction=COLUMN, alignment=CENTER))
        main_box.add(self.result_box_2)

        scroll_container = toga.ScrollContainer(horizontal=False)
        scroll_container.content = main_box

        self.main_window.content = scroll_container
        self.main_window.show()

    def add_image(self, main_box, image_path, padding_top):
        try:
            image = toga.Image(image_path)
            label_image = toga.ImageView(
                image, style=Pack(padding_top=padding_top))
            main_box.add(label_image)
        except Exception as e:
            print(f"Erreur lors du chargement de l'image : {e}")

    def add_label(self, main_box, text, font_size=12):
        instruction_box = toga.Box(style=Pack(
            alignment=CENTER, direction=COLUMN))
        instruction_label = toga.Label(text, style=Pack(
            text_align=CENTER, font_size=font_size))
        instruction_box.add(instruction_label)
        main_box.add(instruction_box)

    def add_input(self, main_box, label_text, padding_top=0):
        input_box = toga.Box(style=Pack(alignment=CENTER, direction=COLUMN))
        input_label = toga.Label(label_text, style=Pack(
            text_align=CENTER, padding_top=padding_top))
        input_field = toga.TextInput(style=Pack(text_align=CENTER, width=50))
        input_box.add(input_label)
        input_box.add(input_field)
        main_box.add(input_box)
        return input_field

    async def calculer_cotes(self, widget):
        self.result_box.clear()
        self.result_box.add(toga.Label("Calcul en cours...",
                            style=Pack(text_align=CENTER)))
        await asyncio.sleep(0.1)

        try:
            longueur_m = self.validate_input(self.longueur_input.value)
            cote_mini_cm = self.validate_input(self.cote_mini_input.value)
            cote_maxi_cm = self.validate_input(self.cote_maxi_input.value)
        except ValueError:
            self.result_box.clear()
            self.result_box.add(toga.Label(
                "Entrées invalides. Veuillez réessayer.", style=Pack(text_align=CENTER)))
            return

        result_text = await asyncio.to_thread(self.perform_calculation_cotes, longueur_m, cote_mini_cm, cote_maxi_cm)
        self.update_results(self.result_box, result_text)

    async def calculer_paquets(self, widget):
        self.result_box_2.clear()
        self.result_box_2.add(toga.Label(
            "Calcul en cours...", style=Pack(text_align=CENTER)))
        await asyncio.sleep(0.1)

        try:
            largeur_toiture_m = self.validate_input(
                self.largeur_toiture_input.value)
            largeur_tuile_cm = self.validate_input(
                self.largeur_tuile_input.value)
            tuiles_par_paquet = self.validate_input(
                self.tuiles_par_paquet_input.value)
            largeur_min_paquet_cm = self.validate_input(
                self.largeur_min_paquet_input.value)
            largeur_max_paquet_cm = self.validate_input(
                self.largeur_max_paquet_input.value)
            largeur_toiture_cm = largeur_toiture_m * 100
        except ValueError:
            self.result_box_2.clear()
            self.result_box_2.add(toga.Label(
                "Entrées invalides. Veuillez réessayer.", style=Pack(text_align=CENTER)))
            return

        result_text = await asyncio.to_thread(self.perform_calculation_paquets, largeur_toiture_cm, largeur_tuile_cm, tuiles_par_paquet, largeur_min_paquet_cm, largeur_max_paquet_cm)
        self.update_results(self.result_box_2, result_text)

    def perform_calculation_cotes(self, longueur_m, cote_mini_cm, cote_maxi_cm):
        cotes_possibles = trouver_cotes_possibles(
            longueur_m, cote_mini_cm, cote_maxi_cm)
        if not cotes_possibles:
            return ["Aucune division possible trouvée."]
        result_text = [f"{div} cm: {
            n} divisions" for div, n in cotes_possibles]
        return result_text

    def perform_calculation_paquets(self, largeur_toiture_cm, largeur_tuile_cm, tuiles_par_paquet, largeur_min_paquet_cm, largeur_max_paquet_cm):
        results = calculer_paquets_de_tuiles(
            largeur_toiture_cm, largeur_tuile_cm, tuiles_par_paquet, largeur_min_paquet_cm, largeur_max_paquet_cm)
        return results

    def validate_input(self, value):
        try:
            return float(value)
        except ValueError:
            raise ValueError("Invalid input")

    def update_results(self, result_box, result_text):
        result_box.clear()
        for line in result_text:
            result_box.add(toga.Label(line, style=Pack(text_align=CENTER)))


def main():
    icon_path = 'resources/my_icon.png'  # Chemin vers votre icône
    return Calculateurdepureau("Pureau-Calculateur", "org.beeware.pureau", icon=icon_path)


if __name__ == "__main__":
    main().main_loop()
