import java.util.List;

public class test {
  private static final int RED = 0;

  class Widget {
    public int getWeight() {
      return 0;
    }
  }

  public static void main(String[] args) {
    List<Integer> transactionsIds = widgets.stream()
        .filter(b -> b.getColor() == test.RED)
        .sorted((x, y) -> x.getWeight() - y.getWeight())
        .mapToInt(Widget::getWeight)
        .sum();
    System.out.println(transactionsIds);
  }
}