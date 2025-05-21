// find_vetrino.cpp : soluzione per scorrere una colonna acquisita e individuare dove inizia e termina il vetrino per
// ridurre il tempo e la memoria necessaria per l'acquisizione.
//L'algoritmo si basa sul fatto che quando inizia e termina il vetrino possiamo trovare nell'immagine uno spesso bordo nero, mentre
//il resto delle foto sono per lo piu bianche a causa della luce riflessa.
//Utilizzo quindi questi riferimenti per individuare la zona dove inizia il vetrino e la zona dove termina.
//L'algoritmo restituisce le coordinate che potranno poi essere usate come parmetri di input per l'acquisizione 
//col microscopio.

#include <opencv2/opencv.hpp>
#include <iostream>
#include <filesystem>
#include <fstream>

using namespace cv;
using namespace std;
using namespace std::filesystem;

const int STEPx5 = 820; // passo da fare per immagini con microscopio x5
const int MAXROW = 52000; //riga massima in cui mettere un vetrino
const int MINROW = 2460; // prima riga utile per mettere un vetrino

struct Rows {
    int startRow;
    int endRow;
};

int main() {
    path directory = "debugCol";
    if (!exists(directory)) {
        cout << "Cartella " << directory << " non trovata"<< endl;
        return -1;
    }

    path imagepath; 
    string path;

    Mat img; //parto da questa posizione perche le righe precedenti non sono valide per posizionare il vetrino
    int i = MINROW;
    int blackPixel, start = -1, end = -1;
    do {
        blackPixel = 0;

        imagepath = directory / (to_string(i) + ".4.jpg");
        path = imagepath.string();
        //cout << path;
        img = imread(path);
        if (img.empty() && i < MAXROW) {   //per aver completato la scansione deve essere arrivato alla riga 52000
            cout << "Immagine non trovata!\n";
            return -1;
        }
        else if (img.empty()){
            cout << "Analisi terminata\n";
            break;
        }

        Mat greyIm;
        cvtColor(img, greyIm, COLOR_BGR2GRAY);

        Rect reduceImg(10, 0, 1, greyIm.rows);
        Mat smallGreyIm = greyIm(reduceImg);

        for (int y = 0; y < smallGreyIm.rows; y++) {
            uchar pixelValue = smallGreyIm.at<uchar>(y, 0);
            if (pixelValue < 50) {
                blackPixel++;
            }
        }
        //cout << "Il numero di pixel e'" << blackPixel << endl;

        if (blackPixel > 30 && start < 0) { // quando troviamo una prima colonna nera inizia il vetrino
            start = i;
            cout << "La colonna di inizio vetrino e' " << start << endl;
        }
        else if (blackPixel > 30 && start > 0 && start != i - STEPx5) { //alla seconda colonna nera finisce il vetrino
            //includo la terza condizione perche il nero potrebbe essere diviso tra 2 immagini all'inizio
            end = i;
            cout << "La colonna di fine vetrino e' " << end << endl;
            return 1;
        }
        i += STEPx5;

    } while (true);

    cout << "Errore nell'individuazione\n";
    //imshow("Immagine", img);
    //waitKey(0);
    return 0;
}

