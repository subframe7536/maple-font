public class test {
    public static void main(String[] args){
        List<Integer> transactionsIds =  widgets.stream()
            .filter(b -> b.getColor() == RED)
            .sorted((x,y) -> x.getWeight() - y.getWeight())
            .mapToInt(Widget::getWeight)
            .sum();
        System.out.println(transactionsIds);
    }
}