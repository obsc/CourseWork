import java.io.IOException;


public class Main {

	public static void main(String[] args) throws IOException {
		int nanimals = 40;
		  for (int i=0; i<10000; i++) {
		   Simulator.main(new String[] { "MyNaturalist", "--seed=" + i,
		     "--nanimals="+nanimals, "--ntrees=70", "--headless"});
		  }
	}

}
